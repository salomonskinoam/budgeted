"""Fast pre-build sanity: the prompt was injected (placeholder gone)."""
from pathlib import Path

t = Path("/root/src/task.yaml").read_text()
assert "<PLACEHOLDER>" not in t, "task.yaml still has <PLACEHOLDER> (prompt was not injected)"
print("check_build OK")
