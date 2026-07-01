from tasks_def.budgeted_tep import BUDGETED_TEP


def grade(transcript: str = "") -> object:
    return BUDGETED_TEP.grade(transcript)
