import warnings
import timeit
try:
    from local_settings import *
except ImportError:
    from settings import *
from functools import wraps


def timetrack(label):
    """Utility function decorator for tracking execution time."""
    def timetrack_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time_point = timeit.default_timer()
            func(*args, **kwargs)
            print(label + ': {sec:.3} seconds.'.format(sec=timeit.default_timer() - time_point))
        return wrapper
    return timetrack_decorator


def suppress_warnings(func):
    """Utility function decorator to suppress warnings (in this case, probably just InsecureRequestWarning)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if SUPPRESS_WARNINGS:
            with warnings.catch_warnings():  # NB: warnings disabled
                warnings.filterwarnings("ignore")
                func(*args, **kwargs)
        else:
            func(*args, **kwargs)
    return wrapper
