from hypothesis.typeclass import TypeClass
from typing import List, Tuple, Union


def test_can_map_concrete_types():
    x = TypeClass()
    x.instance(int, 1)
    x.instance(str, 2)
    assert x[int] == 1
    assert x[str] == 2


def test_can_map_generic_types():
    x = TypeClass()
    x.instance(int, 1)

    @x.instance(List)
    def type_list(T):
        return T + 1
    assert x[List[int]] == 2
    assert x[List[List[int]]] == 3


def test_can_map_tuples():
    x = TypeClass()
    x.instance(Tuple, lambda *args: tuple(args))
    x.instance(int, 0)
    assert x[Tuple[int, int, Tuple[int]]] == (0, 0, (0,))


def test_can_map_unions():
    x = TypeClass()
    x.instance(Union, lambda *args: tuple(args))
    x.instance(int, 0)
    x.instance(str, 1)
    assert x[Union[int, str]] == (0, 1)
