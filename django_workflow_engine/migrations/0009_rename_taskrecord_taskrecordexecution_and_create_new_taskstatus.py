# Generated by Django 4.1.3 on 2023-03-08 15:25

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_workflow_engine", "0008_remove_taskrecord_broke_flow"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="TaskRecord",
            new_name="TaskRecordExecution",
        ),
        migrations.AlterField(
            model_name="taskrecordexecution",
            name="flow",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="task_executions",
                to="django_workflow_engine.flow",
            ),
        ),
        migrations.AlterField(
            model_name="taskrecordexecution",
            name="executed_by",
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                null=True,
                blank=True,
                related_name="task_executions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]