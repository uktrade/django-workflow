# Generated by Django 4.1.3 on 2023-03-08 15:25
from django.db import migrations


def migrate_from_taskrecordexecutions(apps, schema_editor):
    Flow = apps.get_model("django_workflow_engine", "Flow")
    TaskStatus = apps.get_model("django_workflow_engine", "TaskStatus")
    Target = apps.get_model("django_workflow_engine", "Target")
    TaskLog = apps.get_model("django_workflow_engine", "TaskLog")
    TaskRecordExecution = apps.get_model(
        "django_workflow_engine", "TaskRecordExecution"
    )
    TaskRecordExecutionTarget = apps.get_model(
        "django_workflow_engine", "TaskRecordExecutionTarget"
    )
    TaskRecordExecutionTaskLog = apps.get_model(
        "django_workflow_engine", "TaskRecordExecutionTaskLog"
    )

    for flow in Flow.objects.all():
        # For each step in the flow, get the most recent TaskRecordExecution
        # and create a new TaskStatus
        for step in flow.workflow.steps:
            # Get the most recent TaskRecordExecution for this step
            task_execution = (
                TaskRecordExecution.objects.filter(flow=flow, step_id=step.step_id)
                .order_by("-started_at")
                .first()
            )
            task_status = TaskStatus.objects.create(
                flow=flow,
                step_id=step.step_id,
                started_at=task_execution.started_at,
                executed_at=task_execution.executed_at,
                executed_by=task_execution.executed_by,
                task_name=task_execution.task_name,
                task_info=task_execution.task_info,
                done=task_execution.done,
            )

            # Create a new Target for each Target in the TaskRecordExecution
            for target in TaskRecordExecutionTarget.objects.filter(
                task_record=task_execution
            ):
                Target.objects.create(
                    target_string=target.target_string,
                    task_status=task_status,
                )

            # Create a new TaskLog for each TaskLog in the TaskRecordExecution
            for task_log in TaskRecordExecutionTaskLog.objects.filter(
                task_record=task_execution
            ):
                TaskLog.objects.create(
                    logged_at=task_log.logged_at,
                    message=task_log.message,
                    task_status=task_log.task_status,
                )


class Migration(migrations.Migration):
    dependencies = [
        (
            "django_workflow_engine",
            "0010_create_replacement_task_record",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_from_taskrecordexecutions,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
