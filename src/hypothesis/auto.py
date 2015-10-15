from hypothesis.typeclass import TypeClass

import hypothesis.strategies as st
import typing as t
from hypothesis.internal.compat import text_type, binary_type
from hypothesis.conventions import UniqueIdentifier


Arbitrary = TypeClass()

Arbitrary.instance(int, st.integers())
Arbitrary.instance(float, st.floats())
Arbitrary.instance(bool, st.booleans())
Arbitrary.instance(binary_type, st.binary())
Arbitrary.instance(text_type, st.text())


Arbitrary.instance(t.List, st.lists)
Arbitrary.instance(t.Tuple, st.tuples)
Arbitrary.instance(t.Union, st.one_of)
Arbitrary.instance(t.Dict, st.dictionaries)


autoderive = UniqueIdentifier('autoderive')
