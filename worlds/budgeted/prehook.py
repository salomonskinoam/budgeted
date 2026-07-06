"""Thin entrypoint shim: the budgeted tasks' setup.sh call `python -m worlds.budgeted.prehook`. The
projection logic is shared (sdk/mediated/prehook.py); this file only forwards to it so the existing
task setup.sh files need no edit."""
from sdk.mediated.prehook import main

if __name__ == "__main__":
    main()
