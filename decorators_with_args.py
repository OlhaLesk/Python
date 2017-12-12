import functools
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

@trace
def identity(arg):
    return arg

def main():
    result = identity(str)
    trace()

if __name__ == "__main__":
    sys.exit(main())
