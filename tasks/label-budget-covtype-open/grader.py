from tasks_def.label_budget_covtype_open import LABEL_BUDGET_COVTYPE_OPEN


def grade(transcript: str = "") -> object:
    return LABEL_BUDGET_COVTYPE_OPEN.grade(transcript)
