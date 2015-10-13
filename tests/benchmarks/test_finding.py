# coding=utf-8

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# https://github.com/DRMacIver/hypothesis/blob/master/CONTRIBUTING.rst for a
# full list of people who may hold copyright, and consult the git log if you
# need to determine who owns an individual contribution.

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import

import hashlib
import functools

import pytest

import hypothesis.strategies as st
from hypothesis import find, assume
from hypothesis.errors import NoSuchExample

types_to_benchmark = [
    st.text(), st.binary(), st.integers(), st.booleans(),
    st.tuples(st.integers(),),
    st.tuples(st.integers(), st.integers()),
    st.tuples(st.integers(), st.integers(), st.integers()),
    st.integers().flatmap(lambda x: st.tuples(st.just(x), st.integers(x))),
    st.lists(st.floats()),
    st.lists(st.integers()),
    st.lists(st.integers(), unique_by=lambda x: x % 20),
    st.lists(st.integers(), unique_by=lambda x: x % 100),
    st.sets(st.booleans()),
    st.sets(st.integers()),
]


def strategy_benchmark(f):
    @pytest.mark.benchmark(
        max_time=2.0,
    )
    @pytest.mark.parametrize(
        'strategy', types_to_benchmark,
        ids=list(map(repr, types_to_benchmark)))
    @functools.wraps(f)
    def accept(benchmark, strategy):
        return f(benchmark, strategy)
    return accept


@strategy_benchmark
def test_finding_always_true(benchmark, strategy):
    @benchmark
    def result():
        find(strategy, lambda x: True)
    assert result is None


@strategy_benchmark
def test_finding_always_false(benchmark, strategy):
    @benchmark
    def result():
        with pytest.raises(NoSuchExample):
            find(strategy, lambda x: False)
    assert result is None


@strategy_benchmark
def test_finding_always_assumes_false(benchmark, strategy):
    @benchmark
    def result():
        with pytest.raises(NoSuchExample):
            find(strategy, lambda x: assume(False))
    assert result is None


@strategy_benchmark
def test_finding_irrgular_condition(benchmark, strategy):
    @benchmark
    def find_true():
        try:
            find(
                strategy,
                lambda x: hashlib.md5(
                    repr(x).encode('utf-8')).hexdigest()[0] == '0')
        except NoSuchExample:
            pass
