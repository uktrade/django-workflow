"""django_workflow exceptions."""


class WorkflowImproperlyConfigured(Exception):
    pass


class WorkflowError(Exception):
    pass


class WorkflowNotAuthError(Exception):
    def __init__(self, step):
        self.step = step
