from tasks_def.budgeted_diabetes import BUDGETED_DIABETES


def grade(transcript: str = "") -> object:
    return BUDGETED_DIABETES.grade(transcript)
