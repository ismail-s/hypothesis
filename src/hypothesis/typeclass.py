from hypothesis.errors import InvalidArgument, HypothesisException
import typing
import inspect


def _base_and_parameters(typ):
    try:
        return typ.__origin__, typ.__parameters__
    except AttributeError:
        pass
    try:
        return typing.Union, typ.__union_params__
    except AttributeError:
        pass
    try:
        return typing.Tuple, typ.__tuple_params__
    except AttributeError:
        pass
    return typ, ()


class NoMapping(HypothesisException, TypeError):
    pass


class TypeClass(object):
    def __init__(self):
        self.cache = {}
        self.mappings = {}

    def instance(self, target, definition=None):
        origin, params = _base_and_parameters(target)
        if definition is None:
            if params:
                def accept(f):
                    self.instance(target, f)
                    return f
                return accept
            else:
                raise InvalidArgument(
                    "Failed to provide mapping for concrete type %r" % (
                        target,))
        if params:
            if not inspect.isfunction(definition):
                raise InvalidArgument((
                    "Definition for a generic type must be a "
                    "function, but got %r") % (definition,))
        self.mappings[target] = definition

    def __getitem__(self, target):
        try:
            return self.cache[target]
        except KeyError:
            pass
        result = self._do_lookup(target)
        self.cache[target] = result
        return result

    def _do_lookup(self, target):
        if not isinstance(target, type):
            raise InvalidArgument(
                "Expected type argument but got %r of type %r" % (
                    target, type(target)))
        base, params = _base_and_parameters(target)
        if any(isinstance(p, typing.TypeVar) for p in params):
            raise InvalidArgument(
                "Cannot get mapping for generic type %r" % (target,)
            )

        if not params:
            try:
                return self.mappings[target]
            except KeyError:
                raise NoMapping(
                    "No mapping defined for type %r" % (target,)
                )
        try:
            defined_mapping = self.mappings[base]
        except KeyError:
            raise NoMapping(
                "No mapping defined for type %r" % (base,)
            )
        return defined_mapping(*[
            self[p] for p in params
        ])
