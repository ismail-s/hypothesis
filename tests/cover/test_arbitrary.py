from hypothesis.auto import Arbitrary
import typing
from hypothesis.internal.compat import text_type, binary_type
import hypothesis.strategies as st
import pytest
from hypothesis.conventions import UniqueIdentifier


@pytest.mark.parametrize(
    ('typ', 'strategy'), [
        (int, st.integers()),
        (typing.Union[int, text_type], st.integers() | st.text()),
        (binary_type, st.binary()),
        (float, st.floats()),
        (typing.List[bool], st.lists(st.booleans())),
        (typing.Dict[bool, int],
            st.dictionaries(st.booleans(), st.integers()))
    ]
)
def test_arbitrary_strategies(typ, strategy):
    assert repr(Arbitrary[typ]) == repr(strategy)


autoderive = UniqueIdentifier('autoderive')
