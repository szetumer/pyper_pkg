from __future__ import annotations
from collections.abc import Sequence
from itertools import chain
from typing import TypeVar, Callable, TypeAlias, Sequence
from typing import Any
from pyper.nodes import ON, SN, DN

T = TypeVar("T")
U = TypeVar("U")
Input : TypeAlias = SN[T] | list[T] | tuple [T]

def do_nothing() -> Callable[[Input[T]], SN[T]]:
    def identity(ln : Input[T]) -> SN[T]:
            if isinstance(ln, SN):
                return ln
            elif isinstance(ln, list):
                return SN(tuple(ln))
            elif isinstance(ln, tuple):
                return SN(ln)
            else:
                raise TypeError("must be applied to sequence.")
    return identity


class do_func:
    @staticmethod
    def as_filter(f : Callable[[T], bool]) -> Callable[[Input[T]], SN[T]]:
        def filter_func(ln : Input[T]) -> SN[T]:
            data = _get_data(ln)
            return SN(tuple(item for item in data if f(item)))
        return filter_func
    
    @staticmethod
    def on_elets(f : Callable[[T], U]) -> Callable[[Input[T]], SN[U]]:
        def apply_to_elets(ln : Input[T]) -> SN:
            data = _get_data(ln)
            return SN(tuple(f(item) for item in data))
        return apply_to_elets

    @staticmethod
    def naturally(f : Callable[[T], U]) -> Callable[[Input[T]], SN[U]]:
        def apply_to_elets(ln : Input[T]) -> SN:
            data = _get_data(ln)
            return SN(tuple(f(item) for item in data))
        return apply_to_elets    
    
    @staticmethod
    def on_seq(f : Callable[[Sequence[T]], U]) -> Callable[[Input[T]], ON[U]]:
        def return_func(ln : Input[T]) -> ON[U]:
            data : Sequence[T] = _get_data(ln)
            return ON(f(data))
        return return_func
    
    @staticmethod
    def on_wholeseq_to_obj(f : Callable[[Sequence[T]], U]) -> Callable[[Input[T]], ON[U]]:
        def apply_f_to_whole_list(ln : Input[T]) -> ON[U]:
            data : Sequence[T] = _get_data(ln)
            return ON(f(data))
        return apply_f_to_whole_list

    @staticmethod
    def on_wholeseq_to_seq(f : Callable[[Sequence[T]], Sequence[U]]) -> Callable[[Input[T]], SN[U]]:
        def apply_f_to_whole_list(ln : Input[T]) -> SN[U]:
            data : Sequence[T] = _get_data(ln)
            return SN(f(data))
        return apply_f_to_whole_list


class do_flist:
    @staticmethod
    def as_filters(*args : Callable[[T], bool]) -> Callable[[Input[T]],SN[T]]:
        def apply_arg_criteria(node: Input[T]) -> SN[T]:
            l_data = _get_data(node)
            return SN(
                tuple(item for item in l_data if all(tuple(arg(item) for arg in args))
                    ))
        return apply_arg_criteria

    @staticmethod
    def sequentially_on_each_elet(*args : Callable[[T], T]) -> Callable[[Input[T]], SN[T]]:
        def apply_sequentially_to_each(node: Input[T]) -> SN[T]:
            l_data = _get_data(node)
            for f in args:
                l_data = tuple(f(item) for item in l_data)
            return SN(l_data)
        return apply_sequentially_to_each

    @staticmethod #need to fix this one.
    def as_elet_mutations(*args) -> Callable[[ON| SN | list],SN]:
        def apply_sequentially_to_each(node: ON | SN | list) -> SN:
            if isinstance(node, ON) or isinstance(node, SN):
                temp = node.data
            elif isinstance(node, list):
                temp = node
            else:
                raise TypeError("can only apply this func to ONw/list, LN, or list")
            for f in args:
                scratch = tuple(f(item) for item in temp)
                temp = scratch
            return SN(temp)
        return apply_sequentially_to_each

    @staticmethod
    def as_obj_sequentially_to_list(*args : Callable) -> Callable[[Input[T]], SN[Any]]:
        def apply_sequentially_to_each(node: Input[T]) -> Any:
            data = _get_data(node)
            for f in args:
                data = f(data)
            return SN.safe_init(data)
        return apply_sequentially_to_each
    
    @staticmethod
    def on_matching_indicies(*args : Callable[[T], Any]) -> Callable[[Input[T]], SN]:
        def apply_on_matching_indicies(node: Input[T]) -> SN:
            l_data = _get_data(node)
            if len(l_data) != len(args):
                raise ValueError("with matching functions, need the same number as the list node to apply on matching indicies.")
            return SN(tuple(args[i](item) for i, item in enumerate(l_data)))
        return apply_on_matching_indicies

class do_fdict:
    @staticmethod
    def on_wholeseq(**kwargs) -> Callable[[Input[T]], DN]:
        fdict = kwargs
        def apply_each_valfunc_to_list(node: Input[T]) -> DN:
            l_data = _get_data(node)
            result = DN({key : (val(l_data)) for key, val in fdict.items()})
            return result
        return apply_each_valfunc_to_list


def chain_elets() -> Callable[[SN[SN[T]]], SN[T]]:
        def chain_elets_together(node: SN[SN[T]]) -> SN[T]:
            output = chain.from_iterable(tuple(item.data for item in node.data))
            return SN(tuple(output))
        return chain_elets_together

def _get_data(n : Input[T]) -> Sequence[T]: #really should be tuple T, but we don't have that.
    if isinstance(n, SN):
        return n.data
    elif isinstance(n, list):
        return tuple(n)
    elif isinstance(n, tuple):
        return n
    else:
        raise TypeError("on_list only operates on LN, tuples, or lists.")