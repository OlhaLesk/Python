import functools
import time
import sys


def trace(func=None, *, handle=sys.stdout):
    if func is None:
        print("No function")
        return lambda func: trace(func, handle=handle)

    @functools.wraps(func)
    def inner(*args, **kwargs):
        print(func.__name__, args, kwargs,)
        return func(*args, **kwargs)
    return inner

def counted(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        inner.calls_num += 1
        return func(*args, **kwargs)

    inner.calls_num = 0
    return inner

@counted
@trace
def identity(arg):
    return arg

def timethis(func=None, *, iter_numb=100):
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
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not hasattr(inner, "called"):
            func(*args, **kwargs)
            inner.called = True
        inner.called = False
    return inner

@once
def initialize_settings():
    print("Initialized settings.")

def main():
    #to stdout
    #count function calls
    res1 = identity(str)
    print("Calls number: %d" % (identity.calls_num,))
    trace()

    #with time
    print()
    res2 = timethis(sum)(range(10**6))
    print("Sum result: %d" % (res2,))

    #called once
    print()
    initialize_settings()
    initialize_settings()

if __name__ == "__main__":
    sys.exit(main())
