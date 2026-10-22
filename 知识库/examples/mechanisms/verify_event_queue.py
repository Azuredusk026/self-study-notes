"""Run the shared four-check .NET 9 host for the article event queue."""
import json
from pathlib import Path
import runpy


HOST = Path(__file__).resolve().parents[1] / 'revision_16_21/verify_event_queue.py'


def verify():
    """Return the canonical host result; build records remain beside that host."""
    return runpy.run_path(str(HOST))["verify"]()


if __name__ == '__main__':
    print(json.dumps(verify()))
