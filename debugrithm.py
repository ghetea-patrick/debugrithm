from functools import wraps
from pprint import pformat
from sys import exit
from time import strftime
from typing import Callable, NoReturn

type _Func = Callable
type _Void = NoReturn


def _indentprint(func: str, clas: str, text: str, *args, **kwargs) -> None:
    time = strftime("%H%M%S")
    comm = f"{func}@{time}"
    head = ""
    if clas:
        head = f"{clas}.{comm}"
    if text:
        head = f"{head} '{text}'"
    print(head)

    idx = 0
    for arg in args:
        print(f"|{idx}| {arg!r}")
        idx += 1

    for key, val in kwargs.items():
        if isinstance(val, (dict, list)):
            print(f"|{idx}| {key}=")

            form = pformat(val, width=60)
            lins = form.splitlines()
            for lin in lins:
                print(f"| {lin}")
        else:
            print(f"|{idx}| {key}={val}")
        idx += 1


def _quitprogram() -> _Void:
    exit(0)


class Debugger:
    def __init__(self, name: str = "", used: bool = False) -> None:
        self._name = name
        self._used = used

    def stopped(self) -> bool:
        return self._used is False

    def running(self) -> bool:
        return self._used is True

    def pauseit(self) -> None:
        self._used = False

    def startit(self) -> None:
        self._used = True

    def expectthat(self, cond: object, yes: str = "", no: str = "") -> _Void | None:
        if self.stopped():
            return
        if bool(cond):
            _indentprint("expectthat", self._name, yes)
            return
        _indentprint("expectthat", self._name, no)
        _quitprogram()

    def forbidthat(self, cond: object, yes: str = "", no: str = "") -> _Void | None:
        if self.stopped():
            return
        if not bool(cond):
            _indentprint("forbidthat", self._name, yes)
            return
        _indentprint("forbidthat", self._name, no)
        _quitprogram()

    def breakpoint(self, text: str = "", *args, **kwargs) -> _Void | None:
        if self.stopped():
            return
        _indentprint("breakpoint", self._name, text, *args, **kwargs)
        _quitprogram()

    def checkpoint(self, text: str = "", *args, **kwargs) -> None:
        if self.stopped():
            return
        _indentprint("checkpoint", self._name, text, *args, **kwargs)

    def bypasswith(self, curr: object, prev: object, text: str = "") -> object:
        if self.stopped():
            return prev
        _indentprint("breakpoint", self._name, text)
        return curr

    def pingcalled(self, text: str = "", dump: bool = True) -> _Func:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.running():
                    if dump:
                        _indentprint("pingcalled", self._name, text, *args, **kwargs)
                    else:
                        _indentprint("pingcalled", self._name, text)
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def whenproved(self, cond: object, falb: object, yes: str = "", no: str = "") -> _Func:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.stopped():
                    return falb
                if bool(cond):
                    _indentprint("whenproved", self._name, yes)
                else:
                    _indentprint("whenproved", self._name, no)
                return func(*args, **kwargs)
            return wrapper
        return decorator