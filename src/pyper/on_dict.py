from __future__ import annotations
import inspect
from itertools import chain
from typing import TypeVar, Callable, TypeAlias, Type
from typing import Any
from pyper.nodes import ON, SN, DN

T = TypeVar("T")
U = TypeVar("U")
Input : TypeAlias = dict[str, T] | DN[T]

def do_nothing() -> Callable[[Input[T]], DN[T]]:
    def identity(dn : Input[T]) -> DN[T]:
        data = _get_data(dn)
        return DN(data)
    return identity


class do_func:
    @staticmethod
    def on_kwargs(f : Callable) -> Callable[[Input[T]], ON]:
        #need to guard against getting keywords not accepted by the function.
        #note: don't give the function args or kwargs.
        param_strings = list(inspect.signature(f).parameters.keys())
        def unwrap_qwargs(dn :Input[T]) -> ON:
                kwargs = _get_data(dn)
                accepted_kwargs = {key : val for key, val in kwargs.items() if key in param_strings}
                return ON(f(**accepted_kwargs))
        return unwrap_qwargs
    
    @staticmethod
    def on_kwargs_no_wrap(f : Callable) -> Callable[[Input[T]], Any]:
        param_strings = list(inspect.signature(f).parameters.keys())
        def unwrap_qwargs(dn : Input[T]) -> Any:
            kwargs = _get_data(dn)
            accepted_kwargs = {key : val for key, val in kwargs.items() if key in param_strings}
            return f(**accepted_kwargs)
        return unwrap_qwargs
    
    @staticmethod
    def to_each_value(f: Callable[[T], U]) -> Callable[[Input[T]], DN[U]]:
        def apply_to_each_value(dn : Input[T]) -> DN[U]:
            kwargs = _get_data(dn)
            resulting_dict = {key : f(val) for key, val in kwargs.items()}
            return DN(resulting_dict)
        return apply_to_each_value
    
    @staticmethod
    def naturally(f: Callable[[T], U]) -> Callable[[Input[T]], DN[U]]:
        def apply_to_each_value(dn : Input[T]) -> DN[U]:
            kwargs = _get_data(dn)
            resulting_dict = {key : f(val) for key, val in kwargs.items()}
            return DN(resulting_dict)
        return apply_to_each_value
    
    @staticmethod
    def on_wholedict(f: Callable[[dict[str,T]], U]) -> Callable[[Input[T]], ON[U]]:
        def apply_to_whole_dict(dn : Input[T]) -> ON[U]:
            d = _get_data(dn)
            resulting_object = f(d)
            return ON(resulting_object)
        return apply_to_whole_dict
    
    @staticmethod
    def on_wholedict_to_obj(f : Callable[[dict[str,T]], U]) -> Callable[[Input[T]], ON[U]]:
        def apply_to_whole_dict(dn : Input[T]) -> ON[U]:
            d = _get_data(dn)
            resulting_object = f(d)
            return ON(resulting_object)
        return apply_to_whole_dict

class do_flist:
     pass


class do_fdict:
    @staticmethod
    def on_keymatch(**kwargs) -> Callable[[Input[Any]], DN[Any]]:
        fdict = kwargs
        def key_match(dn: Input[Any]) -> DN[Any]:
            input = _get_data(dn)
            #use the same keys on the fdict as the values
            output = DN({key : (val(input[key]) if key in input.keys() else val) for key, val in fdict.items()})
            return output
        return key_match
    
    @staticmethod
    def _qwarg(f : Callable) -> Callable:
        #this creates a guarded f that accepts all qwargs
        param_strings = list(inspect.signature(f).parameters.keys())
        def qwarged_f(**kwargs):
            kwarg_keys = list(kwargs.keys())
            for needed_key in param_strings:
                if needed_key not in kwarg_keys:
                    raise KeyError("must provide all parrameters to all functions in fdict on dict")
            accepted_kwargs = {key : val for key, val in kwargs.items() if key in param_strings}
            result = f(**accepted_kwargs)
            return result
        return qwarged_f
    
    @staticmethod
    def _get_qwargs(f : Callable) -> list[str]:
        return list(inspect.signature(f).parameters.keys())

    @staticmethod
    def on_kwargs(**kwargs) -> Callable[[Input[Any]], DN]:
        fdict = kwargs
        kwarged_fdict = {key : do_fdict._qwarg(val) for key, val in fdict.items()}
        def apply_kwargs_to_all_funcs(dn: Input[Any]) -> DN:
            input = _get_data(dn)
            output = {key : val(**input) for key, val in kwarged_fdict.items()}
            return DN(output)
        return apply_kwargs_to_all_funcs

    @staticmethod
    def on_kwargs_drop_input(**kwargs) -> Callable[[Input[Any]], DN]:
        fdict = kwargs
        kwarged_fdict = {key : do_fdict._qwarg(val) for key, val in fdict.items()}
        def apply_kwargs_to_all_funcs(dn: Input[Any]) -> DN:
            input = _get_data(dn)
            output = {key : val(**input) for key, val in kwarged_fdict.items()}
            return DN(output)
        return apply_kwargs_to_all_funcs

    @staticmethod
    def on_wholedict(**kwargs) -> Callable[[Input[Any]], DN]:
        fdict = kwargs
        def on_whole_dict(dn: Input[Any]) -> DN:
            input = _get_data(dn)
            #use the same keys on the fdict as the values
            output = DN({key : val(input) for key, val in fdict.items()})
            return output
        return on_whole_dict


def chain_vals() -> Callable[[Input[Any]], SN]:
        def chain_vals_together(dn: Input) -> SN:
            if isinstance(dn, DN):
                input = dn.data
            elif isinstance(dn, ON) and isinstance(dn.data, dict):
                input = dn.data
            elif isinstance(dn, dict):
                input = dn
            else:
                raise TypeError("filter pipe must be on LN or ON.")
            output = chain.from_iterable(tuple(input.values()))
            #historically would not give correct order necessarily.
            return SN(tuple(output))
        return chain_vals_together

def type_check(T : Type) -> Callable[[Input[Any]], DN[T]]:
    def type_check_T(dn : Input[Any]) -> DN[T]:
        data = _get_data(dn)
        for value in data.values():
            if not isinstance(value, T):
                raise TypeError(f"dynamic type check revealed DN doesnt contain exclusively {T}-typed values.")
        return DN(data)
    return type_check_T




def _get_data(n : Input[T]) -> dict[str,T]:
    if isinstance(n, DN):
        return n.data
    return n