import pytest
from django_workflow_engine import COMPLETE, Step, Task, Workflow
from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.utils import set_up_flow


class BasicTask(Task):
    task_name = "basic_task"
    auto = True

    def execute(self, task_info):
        return None, {}, True


@pytest.mark.django_db(transaction=True)
def test_parallel_path_join_up_workflow(settings):
    test_workflow = Workflow(
        name="test_workflow",
        steps=[
            Step(
                step_id="start",
                task_name="basic_task",
                start=True,
                targets=["task_a", "task_b"],
            ),
            Step(
                step_id="task_a",
                task_name="basic_task",
                targets=["meet_up"],
            ),
            Step(
                step_id="task_b",
                task_name="basic_task",
                targets=["meet_up"],
            ),
            Step(
                step_id="meet_up",
                task_name="basic_task",
                targets=COMPLETE,
            ),
        ],
    )

    flow, executor, test_user = set_up_flow(
        settings,
        test_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 5

    correct_task_order = [
        "start",
        "task_a",
        "meet_up",
        "task_b",
        "meet_up",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]