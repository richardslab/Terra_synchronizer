import re


class NameFilter:
    def __init__(self, values: list, regexps: list):
        self.values = values
        self.regexps = regexps

        self.values_set: set = set(values)
        self.re_set: set = set([re.compile(regexp) for regexp in regexps])

    def filter(self, name):
        if name in self.values_set:
            return True
        for re_compiled in self.re_set:
            if re_compiled.match(name):
                return True
        return False
