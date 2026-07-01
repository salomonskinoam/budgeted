"""Repo CLI entry: register this repo's tasks, then run the generic SDK CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tasks_def  # noqa: E402,F401  importing registers every task instance
from sdk.cli.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
