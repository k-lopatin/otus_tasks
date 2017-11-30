#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable():
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    return


def decorator(func_1):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''

    def fn_wrapper(fn):
        def wrapper(*args):
            return fn(*args)
        update_wrapper(wrapper, func_1)
        return wrapper
    update_wrapper(fn_wrapper, func_1)
    return fn_wrapper


def countcalls(fn):
    '''Decorator that counts calls made to the function decorated.'''

    @decorator(fn)
    def wrapper(*args):
        if not hasattr(fn, 'calls'):
            fn.calls = 1
        else:
            fn.calls += 1
        wrapper.calls = fn.calls
        return fn(*args)

    return wrapper


def memo(fn):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''

    @decorator(fn)
    def wrapper(*args):
        args_val = ' '.join(map(lambda x: str(x), args))
        if not hasattr(fn, 'saved_args'):
            fn.saved_args = {
                args_val: fn(*args)
            }
        else:
            if args_val not in fn.saved_args:
                fn.saved_args[args_val] = fn(*args)
        update_wrapper(wrapper, fn)
        return fn.saved_args[args_val]
    return wrapper


def n_ary(fn):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''

    def wrapper(*args):
        if len(args) > 2:
            return fn(args[0], wrapper(*args[1:]))
        return fn(*args)

    return wrapper


def fn_call_str(fn, args):
    return fn.__name__ + '(' + ''.join(map(lambda x: str(x), args)) + ')'


def trace(symb):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

     ->>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    def fn_wrapper(fn):

        @decorator(fn)
        def wrapper(*args):
            if not hasattr(fn, 'level'):
                fn.level = 0
                print('->>>' + fn_call_str(fn, args))
            else:
                fn.level += 1

            level_str = ''
            for i in range(0, fn.level):
                level_str += symb

            level_str += ' --> ' + fn_call_str(fn, args)
            print(level_str)

            res = fn(*args)

            level_str = ''
            for i in range(0, fn.level):
                level_str += symb

            level_str += ' <-- ' + fn_call_str(fn, args) + ' == ' + str(res)
            print(level_str)
            fn.level -= 1
            return res
        return wrapper

    return fn_wrapper


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@memo
@trace("####")
def fib(n):
    '''Some doc'''
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print foo(4, 3)
    print foo(4, 3, 2)
    print foo(4, 3, 2, 8)
    print "foo was called", foo.calls, "times"

    print bar(4, 3)
    print bar(4, 3, 2)
    print bar(4, 3, 2, 1)
    print "bar was called", bar.calls, "times"

    print fib.__doc__
    fib(4)
    print fib.calls, 'calls made'


if __name__ == '__main__':
    main()
