from tasks_def.budgeted_covtype import BUDGETED_COVTYPE


def grade(transcript: str = "") -> object:
    return BUDGETED_COVTYPE.grade(transcript)
