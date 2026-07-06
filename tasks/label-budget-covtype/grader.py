from tasks_def.label_budget_covtype import LABEL_BUDGET_COVTYPE


def grade(transcript: str = "") -> object:
    return LABEL_BUDGET_COVTYPE.grade(transcript)
