import csv
import time
from pathlib import Path

from pyoneai.tests.performance.config import REPORT_DIR


class measure_time:
    elapsed_time: int

    def __enter__(self):
        self.start_time = time.monotonic()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed_time = time.monotonic() - self.start_time


def measure_multiple_executions(fun, trials):
    times = []
    for _ in range(trials):
        with measure_time() as mt:
            fun()
        times.append(mt.elapsed_time)
    return times


def save_result(exp_dir, result):
    target_file = Path(REPORT_DIR) / exp_dir
    target_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "predictiom_model",
        "vm_id",
        "avg_time",
        "std_time",
    ]
    if not target_file.exists():
        with open(target_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    with open(target_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows([result])
