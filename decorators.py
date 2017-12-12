import functools
import time
import sys
import warnings


# DECORATORS
def trace(func=None, *, handle=sys.stdout):
    """Decorator with optional argument."""
    if func is None:
        print("No function")
        return lambda func: trace(func, handle=handle)

    @functools.wraps(func)
    def inner(*args, **kwargs):
        print(func.__name__, args, kwargs,)
        return func(*args, **kwargs)
    return inner

def counted(func):
    """Count function calls."""
    @functools.wraps(func)
    def inner(*args, **kwargs):
        inner.calls_num += 1
        return func(*args, **kwargs)

    inner.calls_num = 0
    return inner

def timethis(func=None, *, iter_numb=100):
    """Count time of work."""
    if func is None:
        print("No function")
        return lambda func: timethis(func, iter_numb=iter_numb)

    @functools.wraps(func)
    def inner(*args, **kwargs):
        print(func.__name__, end=" time: ")
        acc = float("inf")
        for i in range(iter_numb):
            tick = time.perf_counter()
            result = func(*args, **kwargs)
            acc = min(acc, time.perf_counter() - tick)
        print(acc)
        return result
    return inner

def once(func):
    """Allow func to be called once."""
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not hasattr(inner, "called"):
            func(*args, **kwargs)
            inner.called = True
        inner.called = False
    return inner

def memoized(func):
    """Memorize the results of function calls."""
    cache = {}

    @functools.wraps(func)
    def inner(*args, **kwargs):
        key = args + tuple(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return inner

#Functions
@counted
@trace
def identity(arg):
    return arg

@once
def initialize_settings():
    print("Initialized settings.")

@memoized
def ackermann(m, n):
    if not m:
        return n + 1
    elif not n:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))

def main():
    #to stdout
    #count function calls
    identity(str)
    print("Calls number: %d" % (identity.calls_num,))
    trace()

    #with time
    print()
    print("Sum result: %d" % (timethis(sum)(range(10**6)),))

    #called once
    print()
    initialize_settings()
    initialize_settings()

    #memoized
    print()
    print(ackermann(3, 4))

if __name__ == "__main__":
    sys.exit(main())
