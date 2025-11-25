import time


def parse_timedelta_str_to_seconds(timedelta_str: str) -> int:
    try:
        return int(timedelta_str)
    except ValueError:
        pass
    UNITS = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 24 * 3600,
        "w": 7 * 24 * 3600,
        "M": 30 * 24 * 3600,  # Approximation for month
    }
    unit = timedelta_str[-1]
    return int(timedelta_str[:-1]) * UNITS.get(unit, 1)


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
