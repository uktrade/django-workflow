# Django Workflow Engine
`django-workflow-engine` is a lightweight and reusable workflow engine for
Django applications. It enables you to better organise the business logic for
collaborating users.

## Installation

    pip install django-workflow-engine

## Getting started
Add the application to your Django settings `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    ...
    "django_workflow_engine",
]
```

Add the built-in `django-workflow-engine` view urls to your project's `urls.py` as follows:


```python
from django_workflow_engine import workflow_urls
...
urlpatterns = [
    path("workflow/", workflow_urls()),
    ...
]
```

This will utilise all `django-workflow-engine` built-in view classes. Default views are:

- `list_view=FlowListView` List of workflow instances view.
- `view=FlowView` Workflow instance view.
- `create_view=FlowCreateView` Create workflow view.
- `continue_view=FlowContinueView` Workflow continuation view.
- `diagram_view=FlowDiagramView` Workflow diagram view.

You can override any the built-in view classes with your own, for example to
provide your own view classes for flow list and flow view:

```python
urlpatterns = [
        path("workflow/",
             workflow_urls(
                 list_view=MyFlowListView,
                 view=MyFlowView,
            ),
        ),
    ]
```

## Building your first workflow

Create a `workflows.py` in your project and add your uniquely named workflows.

```python
from django_workflow_engine import Step, Workflow

onboard_contractor = Workflow(
    name="onboard_contractor",
    steps=[
        Step(...),
        Step(...),
        Step(...),
    ],
)

onboard_perm = Workflow(
    name="onboard_perm",
    steps=[
        ...
    ],
)
```

Add you workflows to your Django settings as follows:

```python
DJANGO_WORKFLOWS = {
    "onboard_contractor": "your_app.workflows.onboard_contractor",
    "onboard_perm": "your_app.workflows.onboard_perm",
}
```

Each entry needs to be a valid module path where the final component is the
name of your workflow class.

Finally, run the `django-workflow-engine` migrations:

```bash
$ ./manage.py migrate
```
