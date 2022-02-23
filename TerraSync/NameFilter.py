import re
from typing import Pattern


class NameFilter:
    def __init__(self, values: list[str], regexps: list[str]):
        self.values = values
        self.regexps = regexps

        self.values_set: set[str] = set(values)
        self.re_set: set[Pattern] = set([re.compile(regexp) for regexp in regexps])

    def filter(self, name):
        if name in self.values_set:
            return True
        for re_compiled in self.re_set:
            if re_compiled.match(name):
                return True
        return False
