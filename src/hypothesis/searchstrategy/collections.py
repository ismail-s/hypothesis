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

from __future__ import division, print_function, absolute_import

import math
from copy import deepcopy
from random import Random
from collections import namedtuple

import hypothesis.internal.conjecture.utils as d
from hypothesis.control import assume
from hypothesis.utils.show import show
from hypothesis.utils.size import clamp
from hypothesis.internal.compat import hrange, OrderedDict, integer_types
from hypothesis.searchstrategy.strategies import SearchStrategy, \
    one_of_strategies, MappedSearchStrategy


class TupleStrategy(SearchStrategy):

    """A strategy responsible for fixed length tuples based on heterogenous
    strategies for each of their elements.

    This also handles namedtuples

    """

    def __init__(self,
                 strategies, tuple_type):
        SearchStrategy.__init__(self)
        strategies = tuple(strategies)
        self.tuple_type = tuple_type
        self.element_strategies = strategies

    def __repr__(self):
        if len(self.element_strategies) == 1:
            tuple_string = u'%s,' % (repr(self.element_strategies[0]),)
        else:
            tuple_string = u', '.join(map(repr, self.element_strategies))
        return u'TupleStrategy((%s), %s)' % (
            tuple_string, self.tuple_type.__name__
        )

    def newtuple(self, xs):
        """Produce a new tuple of the correct type."""
        if self.tuple_type == tuple:
            return tuple(xs)
        else:
            return self.tuple_type(*xs)

    def do_draw(self, data):
        return self.newtuple(
            data.draw(e) for e in self.element_strategies
        )


class ListStrategy(SearchStrategy):

    """A strategy for lists which takes an intended average length and a
    strategy for each of its element types and generates lists containing any
    of those element types.

    The conditional distribution of the length is geometric, and the
    conditional distribution of each parameter is whatever their
    strategies define.

    """

    Parameter = namedtuple(
        u'Parameter', (u'child_parameter', u'average_length')
    )

    def __init__(
        self,
        strategies, average_length=50.0, min_size=0, max_size=float(u'inf')
    ):
        SearchStrategy.__init__(self)

        assert average_length > 0
        self.average_length = average_length
        strategies = tuple(strategies)
        self.min_size = min_size or 0
        self.max_size = max_size or float('inf')
        if strategies:
            self.element_strategy = one_of_strategies(strategies)
        else:
            self.element_strategy = None

    def do_draw(self, data):
        stopping_value = 255 - d.byte(data)
        result = []
        while len(result) < self.max_size:
            data.start_example()
            probe = d.byte(data)
            if probe <= stopping_value:
                if len(result) < self.min_size:
                    data.draw(self.element_strategy)
                    data.stop_example()
                    continue
                else:
                    data.stop_example()
                    break
            result.append(data.draw(self.element_strategy))
            data.stop_example()
        return result

    def __repr__(self):
        return (
            u'ListStrategy(%r, min_size=%r, average_size=%r, max_size=%r)'
        ) % (
            self.element_strategy, self.min_size, self.average_length,
            self.max_size
        )


class UniqueListStrategy(SearchStrategy):

    def __init__(
        self,
        elements, min_size, max_size, average_size,
        key
    ):
        super(UniqueListStrategy, self).__init__()
        assert min_size <= average_size <= max_size
        self.min_size = min_size
        self.max_size = max_size
        self.average_size = average_size
        self.element_strategy = elements
        self.key = key

    def do_draw(self, data):
        seen = set()
        stopping_value = d.byte(data)
        result = []
        while len(result) < self.max_size:
            data.start_example()
            probe = d.byte(data)
            if probe <= stopping_value:
                if len(result) < self.min_size:
                    data.draw(self.element_strategy)
                    data.stop_example()
                    continue
                else:
                    data.stop_example()
                    break
            value = data.draw(self.element_strategy)
            data.stop_example()
            k = self.key(value)
            if k in seen:
                continue
            seen.add(k)
            result.append(value)
        return result


class FixedKeysDictStrategy(MappedSearchStrategy):

    """A strategy which produces dicts with a fixed set of keys, given a
    strategy for each of their equivalent values.

    e.g. {'foo' : some_int_strategy} would
    generate dicts with the single key 'foo' mapping to some integer.

    """

    def __init__(self, strategy_dict):
        self.dict_type = type(strategy_dict)

        if isinstance(strategy_dict, OrderedDict):
            self.keys = tuple(strategy_dict.keys())
        else:
            try:
                self.keys = tuple(sorted(
                    strategy_dict.keys(),
                ))
            except TypeError:
                self.keys = tuple(sorted(
                    strategy_dict.keys(), key=show,
                ))
        super(FixedKeysDictStrategy, self).__init__(
            strategy=TupleStrategy(
                (strategy_dict[k] for k in self.keys), tuple
            )
        )

    def __repr__(self):
        return u'FixedKeysDictStrategy(%r, %r)' % (
            self.keys, self.mapped_strategy)

    def pack(self, value):
        return self.dict_type(zip(self.keys, value))
