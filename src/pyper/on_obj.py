from __future__ import annotations
from collections.abc import Sequence
from typing import Callable, Any, TypeVar, TypeAlias, Type
from pyper.nodes import ON, SN, DN

T = TypeVar("T")
U = TypeVar("U")
Input : TypeAlias = ON[T] | T

class do_func:
    @staticmethod
    def giving_seq(f : Callable[[T], Sequence[U]]) -> Callable[[Input[T]], SN[U]]:
        def apply_f(n : Input[T]) -> SN[U]:
            data = _get_data(n)
            return SN.safe_init(f(data)) #safe because we don't know whether the function
        #will give us a tuple or not.
        return apply_f
    
    @staticmethod
    def to_seq(f : Callable[[T], Sequence[U]]) -> Callable[[Input[T]], SN[U]]:
        def apply_f(n : Input[T]) -> SN[U]:
            data = _get_data(n)
            return SN.safe_init(f(data)) #safe because we don't know whether the function
        #will give us a tuple or not.
        return apply_f
    
    @staticmethod
    def naturally(f : Callable[[T], U] ) -> Callable[[Input[T]], ON[U]]:
        def apply_f(n: Input[T]) -> ON[U]:
            data = _get_data(n)
            return ON(f(data))
        return apply_f
    
    @staticmethod
    def giving_on(f : Callable[[T], U] ) -> Callable[[Input[T]], ON[U]]:
        def apply_f(n: Input[T]) -> ON[U]:
            data = _get_data(n)
            return ON(f(data))
        return apply_f


class do_flist:
    @staticmethod
    def does_obj_pass_all_flist_criteria(*args : Callable[[T], bool]) -> Callable[[Input[T]], bool]:
        def apply_arg_criteria(n: Input[T]) -> bool:
            data = _get_data(n)
            return all([f(data) for f in args])
        return apply_arg_criteria
    
    @staticmethod
    def eletfuncs_on_obj(*args : Callable[[T], U]) -> Callable[[Input[T]], SN[U]]:
        def apply_each_arg(n: Input[T]) -> SN[U]:
            flist = args
            data = _get_data(n)
            return SN(tuple(f(data) for f in flist))
        return apply_each_arg

    @staticmethod
    def naturally(*args : Callable[[T], U]) -> Callable[[Input[T]], SN[U]]:
        def apply_each_arg(n: Input[T]) -> SN[U]:
            flist = args
            data = _get_data(n)
            return SN(tuple(f(data) for f in flist))
        return apply_each_arg
    
    @staticmethod
    def sequentially(*args : Callable[[T], T]) -> Callable[[Input[T]], ON[T]]:
        def apply_sequentially(n : Input[T]) -> ON[T]:
            data = _get_data(n)
            for f in args:
                data = f(data)
            return ON(data)
        return apply_sequentially


class do_fdict:
    @staticmethod
    def naturally(**kwargs) -> Callable[[Input[T]],DN]:
        def val_funcs(obj_node : Input[T]) -> DN:
            fdict = kwargs
            #if the item in the dictionary is not callable, just return it.
            if isinstance(obj_node, ON):
                return DN({key : (val(obj_node.data) if callable(val) else val) for key, val in fdict.items()})
            elif isinstance(obj_node, object):
                return DN({key : (val(obj_node) if callable(val) else val) for key, val in fdict.items()})
            else:
                raise TypeError("pipe application of all criteria must take ON or obj")
        return val_funcs

    @staticmethod
    def by_valfuncs(**kwargs) -> Callable[[Input[T]],DN]:
        def val_funcs(obj_node : Input[T]) -> DN:
            input = kwargs
            if isinstance(obj_node, ON):
                return DN({key : val(obj_node.data) for key, val in input.items()})
            elif isinstance(obj_node, object):
                return DN({key : val(obj_node) for key, val in input.items()})
            else:
                raise TypeError("pipe application of all criteria must take ON or obj")
        return val_funcs


def multiply_by(n : int) -> Callable[[Input[T]], SN[T]]:
    if not n > 0:
        raise ValueError("can only multiply by positive integer")
    def get_multiple(on : Input[T]) -> SN[T]:
        data = _get_data(on)
        return SN(tuple(data for i in range(n)))
    return get_multiple

def type_check(T : Type) -> Callable[[Input[Any]], ON[T]]:
    def type_check_T(on : Input[Any]) -> ON[T]:
        data = _get_data(on)
        if not isinstance(data, T):
            raise TypeError(f"dynamic type check revealed ON doesnt contain a {T}-typed value.")
        return ON(data)
    return type_check_T


def _get_data(n : Input[T]) -> T:
    if isinstance(n, ON):
        return n.data
    return n