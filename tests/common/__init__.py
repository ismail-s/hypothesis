# coding=utf-8
#
# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)
#
# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# https://github.com/DRMacIver/hypothesis/blob/master/CONTRIBUTING.rst for a
# full list of people who may hold copyright, and consult the git log if you
# need to determine who owns an individual contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

import sys
from collections import namedtuple

try:
    import pytest
except ImportError:
    pytest = None

from hypothesis.settings import Settings
from hypothesis.internal.debug import timeout
from hypothesis.strategytests import templates_for
from tests.common.basic import Bitfields
from hypothesis.strategies import integers, floats, just, one_of, \
    sampled_from, streaming, basic, lists, booleans, dictionaries, tuples, \
    frozensets, complex_numbers, sets, text, binary, decimals, fractions, \
    none, randoms, builds, fixed_dictionaries, recursive
from hypothesis.internal.compat import hrange
# from hypothesis.searchstrategy.narytree import n_ary_tree
from hypothesis.utils.show import show


settings = Settings(max_examples=100, timeout=4)

__all__ = [u'small_verifier', u'timeout', u'standard_types', u'OrderedPair']


OrderedPair = namedtuple(u'OrderedPair', (u'left', u'right'))


ordered_pair = integers().flatmap(
    lambda right: integers(min_value=0).map(
        lambda length: OrderedPair(right - length, right)))


def constant_list(strat):
    return strat.flatmap(
        lambda v: lists(just(v)),
    )


EvalledIntStream = streaming(integers()).map(lambda x: list(x[:3]) and x)

ABC = namedtuple(u'ABC', (u'a', u'b', u'c'))


def abc(x, y, z):
    return builds(ABC, x, y, z)

with Settings(average_list_length=10.0):
    standard_types = [
        basic(Bitfields),
        EvalledIntStream,
        lists(max_size=0), tuples(), sets(max_size=0), frozensets(max_size=0),
        fixed_dictionaries({}),
        #n_ary_tree(booleans(), booleans(), booleans()),
        #n_ary_tree(integers(), integers(), integers()),
        abc(booleans(), booleans(), booleans()),
        abc(booleans(), booleans(), integers()),
        templates_for(one_of(*map(just, hrange(10)))),
        fixed_dictionaries({u'a': integers(), u'b': booleans()}),
        dictionaries(booleans(), integers()),
        dictionaries(text(), booleans()),
        one_of(integers(), tuples(booleans())),
        sampled_from(range(10)),
        one_of(just(u'a'), just(u'b'), just(u'c')),
        sampled_from((u'a', u'b', u'c')),
        integers(),
        integers(min_value=3),
        integers(min_value=(-2 ** 32), max_value=(2 ** 64)),
        floats(), floats(min_value=-2.0, max_value=3.0),
        floats(), floats(min_value=-2.0),
        floats(), floats(max_value=-0.0),
        floats(), floats(min_value=0.0),
        floats(min_value=3.14, max_value=3.14),
        text(), binary(),
        booleans(),
        tuples(booleans(), booleans()),
        frozensets(integers()),
        sets(frozensets(booleans())),
        complex_numbers(),
        fractions(),
        decimals(),
        lists(lists(booleans())),
        lists(lists(booleans(), average_size=100)),
        lists(floats(0.0, 0.0), average_size=1.0),
        ordered_pair, constant_list(integers()),
        streaming(integers()).map(lambda x: list(x[:2]) and x),
        integers().filter(lambda x: abs(x) > 100),
        floats(min_value=-sys.float_info.max, max_value=sys.float_info.max),
        none(), randoms(),
        tuples().flatmap(lambda x: EvalledIntStream),
        templates_for(integers(min_value=0, max_value=0).flatmap(
            lambda x: integers(min_value=0, max_value=0))),
        booleans().flatmap(lambda x: booleans() if x else complex_numbers()),
        recursive(
            base=booleans(), extend=lambda x: lists(x, max_size=3),
            max_leaves=10,
        )
    ]


if pytest is not None:
    def parametrize(args, values):
        return pytest.mark.parametrize(
            args, values, ids=list(map(show, values)))
