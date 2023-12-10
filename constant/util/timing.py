# Copyright 2023 O1 Software Network. MIT licensed.


from time import time
from typing import Any, Callable


def timed(
    func: Callable[[Any], Any], reporting_threshold_sec: float = 0.1
) -> Callable[[Any], Any]:
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        t0 = time()
        ret = func(*args, **kwargs)
        elapsed = time() - t0
        if elapsed > reporting_threshold_sec and func.__name__ != "wrapped":
            print(f"  Elapsed time of {elapsed:.3f} seconds for {func.__name__}")
        return ret

    return wrapped