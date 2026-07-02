from tasks_def.budgeted_unsw import BUDGETED_UNSW


def grade(transcript: str = "") -> object:
    return BUDGETED_UNSW.grade(transcript)
