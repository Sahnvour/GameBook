# -*- coding: utf-8 -*-

import re
from random import randint

comparators = {
'=': lambda x, y: x == y,
'>': lambda x, y: x > y,
'<': lambda x, y: x < y,
}

p = re.compile('(\d*)d(\d*)([<>=])(\d*)')


def roll(method):
    try:
        method = method.replace(' ', '')
        if method[-1] == '%':
            x = int(method[:-1])
            return randint(1, 100) < x

        else:
            m = p.match(method)
            dices = m.group(1)
            faces = m.group(2)
            comp = m.group(3)
            thres = m.group(4)
            res = 0
            for i in xrange(0, int(dices)):
                res += randint(1, int(faces))

            return comparators[comp](res, int(thres))
    except:
        raise ValueError("Invalid random event : '" + str(method) + "'")


if __name__ == "__main__":

    for i in xrange(0, 10):
        print roll('2d6>9')