import logging

from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

from django_workflow_engine.exceptions import WorkflowNotAuthError
from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow, TaskRecord
from django_workflow_engine.tasks import TaskError
from django_workflow_engine.utils import build_workflow_choices

logger = logging.getLogger(__name__)


class FlowListView(ListView):
    model = Flow
    paginate_by = 100  # if pagination is desired
    ordering = "-started"


class FlowView(DetailView):
    model = Flow


class FlowCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workflow_name"] = forms.ChoiceField(
            choices=build_workflow_choices(settings.DJANGO_WORKFLOWS)
        )

    class Meta:
        model = Flow
        fields = ["workflow_name", "flow_name"]


class FlowCreateView(CreateView):
    model = Flow
    form_class = FlowCreateForm

    def get_success_url(self):
        return reverse("flow", args=[self.object.pk])

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.executed_by = self.request.user
        response = super().form_valid(form)
        executor = WorkflowExecutor(self.object)
        try:
            executor.run_flow(user=self.request.user)
        except WorkflowNotAuthError as e:
            logger.warning(f"{e}")
            raise PermissionDenied(f"{e}")
        return response


class FlowDeleteView(DeleteView):
    model = Flow
    success_url = reverse_lazy("flow-list")


class FlowContinueView(View):
    cannot_view_step_url = None

    def __init__(self):
        super().__init__()
        self.flow = None
        self.step = None
        self.task = None

    def get_cannot_view_step_url(self):
        return reverse_lazy(
            "flow",
            args=[self.flow.pk],
        )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.flow = Flow.objects.get(pk=kwargs.get("pk"))

        if self.flow.current_task_record:
            self.step = self.flow.workflow.get_step(
                self.flow.current_task_record.step_id
            )

            # Check user can view step
            self.cannot_view_step_url = self.get_cannot_view_step_url()

            # Check user has permission to perform this task
            try:
                WorkflowExecutor.check_authorised(
                    request.user,
                    self.step,
                )
            except WorkflowNotAuthError:
                return redirect(self.cannot_view_step_url)

            self.task = self.step.task(
                request.user, self.flow.current_task_record, self.flow
            )
        elif not self.flow.is_complete:
            logger.info(f"{self.flow.nice_name} is not complete")
            nodes = [step_to_node(self.flow, step) for step in self.flow.workflow.steps]
            for n in nodes:
                if n["data"]["done"] is None:
                    self.step = self.flow.workflow.get_step(n["data"]["id"])
                    self.task = self.step.task(
                        request.user, self.flow.current_task_record, self.flow
                    )
                    task_record, created = TaskRecord.objects.get_or_create(
                        flow=self.flow,
                        task_name=self.step.task_name,
                        step_id=self.step.step_id,
                        executed_by=None,
                        executed_at=None,
                        defaults={"task_info": self.step.task_info or {}},
                    )
                    break

    def get(self, request, pk, **kwargs):
        if not self.task:
            return redirect(reverse("flow-list"))

        context = self.get_context_data()

        template = self.task.template or "django_workflow_engine/flow-continue.html"

        return render(request, template, context=context)

    def post(self, request, **kwargs):
        task_uuid = self.request.POST["uuid"]
        executor = WorkflowExecutor(self.flow)
        try:
            executor.run_flow(
                user=self.request.user,
                task_info=self.request.POST,
                task_uuids=[task_uuid],
            )
        except WorkflowNotAuthError as e:
            logger.warning(f"{e}")
            raise PermissionDenied(f"{e}")
        except TaskError as error:
            template = self.task.template or "django_workflow_engine/flow-continue.html"

            context = self.get_context_data() | error.context

            return render(request, template, context=context)
        return redirect(reverse("flow", args=[self.flow.pk]))

    def get_context_data(self, **kwargs):
        context = {
            "flow": self.flow,
            "step": self.step,
            "task": self.task,
        }
        if not self.task.auto:
            context |= self.task.context()
        return context


class FlowDiagramView(View):
    @staticmethod
    def get(request, pk, **kwargs):
        try:
            flow = Flow.objects.get(pk=pk)
        except Flow.DoesNotExist:
            raise Http404(f"Flow {pk} not found")
        elements = workflow_to_cytoscape_elements(flow)
        return JsonResponse({"elements": elements})


def workflow_to_cytoscape_elements(flow):
    nodes = [step_to_node(flow, step) for step in flow.workflow.steps]

    edges = []
    for step in flow.workflow.steps:
        targets = step.targets
        for target in targets:
            if not target:
                continue

            edges.append(
                {
                    "data": {
                        "id": f"{step.step_id}{target}",
                        "source": step.step_id,
                        "target": target,
                    }
                }
            )

    return [*nodes, *edges]


def step_to_node(flow, step):
    latest_step_task = (
        flow.tasks.order_by("started_at").filter(step_id=step.step_id).last()
    )

    targets = step.targets

    end = not bool(targets)
    done = latest_step_task and latest_step_task.executed_at
    current = latest_step_task and not latest_step_task.executed_at

    label = step.description or format_step_id(step.step_id)
    if end and done:
        label += " ✓"

    return {
        "data": {
            "id": step.step_id,
            "label": label,
            "start": step.start,
            "end": end,
            "decision": len(targets) > 1,
            "done": done,
            "current": current,
        }
    }


def format_step_id(step_id):
    # email_all_users -> Email all users
    return step_id.replace("_", " ").title()
