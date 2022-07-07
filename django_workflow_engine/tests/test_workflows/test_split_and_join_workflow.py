import pytest

from django_workflow_engine.models import TaskRecord
from django_workflow_engine.tests.utils import set_up_flow
from django_workflow_engine.tests.workflows import split_and_join_workflow


@pytest.mark.django_db(transaction=True)
def test_parallel_path_join_up_workflow(settings):
    flow, executor, test_user = set_up_flow(
        settings,
        split_and_join_workflow,
    )
    executor.run_flow(user=test_user)

    assert TaskRecord.objects.count() == 4

    correct_task_order = [
        "start",
        "task_a",
        "task_b",
        "task_c",
    ]

    for i, task_record in enumerate(TaskRecord.objects.all()):
        assert task_record.step_id == correct_task_order[i]
