from tasks_def.budgeted_thyroid import BUDGETED_THYROID


def grade(transcript: str = "") -> object:
    return BUDGETED_THYROID.grade(transcript)
