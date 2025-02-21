from __future__ import annotations
from collections import UserDict
from collections.abc import Sequence
from typing import Callable, Any, Dict, TypeVar, Generic

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

class N:
    def __init__(self, data):
        self.data = data

class ON(Generic[T], N):
    def __init__(self, data : T):
        self.data: T = data

    def apply_dictof(self, **kwargs): #takes pipes
        return DN({key : fval(self) for key, fval in kwargs.items()})
    
    def apply_seqof(self, *args): #takes pipes
        return SN(tuple(f(self) for f in args))

    def to_obj(self, f : Callable[[ON[T]], ON[U]]) -> ON[U]:
        return f(self)

    def to_seq(self, f : Callable[[ON[T]], SN[U]]) -> SN[U]:
        return f(self)
    
    def to_dict(self, f : Callable[[ON[T]], DN[U]]) -> DN[U]:
        return f(self)
    
    def recast_to_sn(self) -> SN[T]:
        if not isinstance(self.data, Sequence):
            raise TypeError("recasting to sequence_node (SN) requires data to be sequence")
        if not isinstance(self.data, tuple):
            return SN(tuple(self.data))
        return SN(self.data)

    def is_on_of(self : ON[Any], t) -> ON[Any]:
        if not isinstance(self.data, t):
            raise TypeError(f"item is not of type {t}")
        return self


class SN(Generic[T], N):
    def __init__(self, data : Sequence[T]) -> None:
        self.data = data
    
    def __iter__(self):
        return self.data.__iter__()
    
    @classmethod
    def safe_init(cls, data : Sequence[T]) -> SN[T]:
        if not isinstance(data, tuple):
            data = tuple(data)
        return cls(data)

    def on_elets(self, f : Callable[[T], U]) -> SN[U]:
        data : Sequence[T] = self.data
        output : Sequence[U] = tuple((f(item) for item in data))
        return SN(output)

    def apply_dictof(self, **kwargs : Callable[[SN[T]], U]) -> DN[U]:
        #the f's have to take an LN function
        return DN({key : f(self) for key, f in kwargs.items()})
    
    def apply_seqof(self, *args :  Callable[[SN[T]], U]) -> SN[U]:
        #the f's have to take an LN function
        return SN(tuple(f(self) for f in args))
    
    def is_seq(self):
        if not isinstance(self.data, tuple):
            raise TypeError("data needs to be tuple")
        return self
    
    def to_seq(self, f : Callable[[SN[T]], SN[U]]) -> SN[U]:
        return f(self)

    def to_obj(self, f : Callable[[SN[T]], ON[U]]) -> ON[U]:
        return f(self)
    
    def to_dict(self, f : Callable[[SN[T]], DN[U]]) -> DN[U]:
        return f(self)
    
    def snon_drop_on(self : SN[ON[T]]) -> SN[T]:
        return SN(tuple(item.data for item in self.data))
    
    def sndn_drop_dn(self : SN[DN[T]]) -> SN[dict[str, T]]:
        return SN(tuple(item.data for item in self.data))
    
    def is_snon(self : SN[Any]) -> SN[ON[Any]]:
        if not isinstance(self, SN):
            raise TypeError("SN is not SN!")
        for item in self.data:
            if not isinstance(item, ON):
                raise TypeError("SN is not SNON")
        return self
    
    def sn_tosnon(self : SN[T]) -> SN[ON[T]]:
        data = self.data
        result = tuple(ON(item) for item in data)
        return SN(result) 
    
    def sn_tosndn(self : SN[dict[str,T]]) -> SN[DN[T]]:
        data = self.data
        result = tuple(DN(item) for item in data)
        return SN(result) 
    
    def is_sndn(self : SN[Any]) -> SN[DN[Any]]:
        if not isinstance(self, SN):
            raise TypeError("SN is not SN!")
        for item in self.data:
            if not isinstance(item, DN):
                raise TypeError("SN is not SNDN")
        return self
    
    def is_snsn(self: SN[Any]) -> SN[SN[Any]]:
        if not isinstance(self, SN):
            raise TypeError("SN is not SN!")
        for item in self.data:
            if not isinstance(item, SN):
                raise TypeError("SN is not SNSN!")
        return self
    
    def is_sn_of(self : SN[Any], t) -> SN[Any]:
        for item in self.data:
            if not isinstance(item, t):
                raise TypeError(f"item is not of type {t}")
        return self
    
class DN(UserDict[str, T], N):
    def __init__(self, data : Dict[str, T]):
        super().__init__(data)

    def on_vals(self, f) -> DN:
        if isinstance(self.data, dict):
            return DN({key : f(val) for key, val in self.data.items()})
        else:
            raise TypeError("can only apply function on_vals of DN.")
    
    def as_kwargs(self, f):
        if isinstance(self.data, dict):
            return f(**self.data)

    def apply_dictof(self, **kwargs) -> DN:
        return DN({key : fval(self) for key, fval in kwargs.items()})
    
    def apply_seqof(self, *args) -> SN:
        return SN(tuple(f(self) for f in args))

    def to_obj(self, f : Callable[[DN[T]], ON[U]]) -> ON[U]:
        return f(self)

    def to_seq(self, f : Callable[[DN[T]], SN[U]]) -> SN[U]:
        return f(self)

    def to_dict(self, f : Callable[[DN[T]], DN[U]]) -> DN[U]:
        return f(self)
    
    def dnsn_to_sndn(self : DN[SN[Any]]) -> SN[DN[Any]]:
        input_d = self.data
        #first check that all items are of the same length.
        first_ln_length = len(list(input_d.values())[0].data)
        for val in input_d.values():
            if len(val.data) != first_ln_length:
                raise TypeError("dnln_to_lndn conversion requires ln's have all same length")
        #now we can index the values by i from 0 to val_len and not go
        #go out of bounds
        output_l = tuple(
            DN({key : val.data[i] for key, val in input_d.items()})
            for i in range(first_ln_length))
        return SN(output_l)
    
    def dnsn_drop_sn(self : DN[SN[T]]) -> DN[Sequence[T]]:
        return DN({key :  val.data for key, val in self.data.items()})
    
    def dnon_drop_on(self :DN[ON[T]]) -> DN[T]:
        return DN({key : val.data for key, val in self.data.items()})
    
    def is_dnsn(self : Any) -> DN[SN[Any]]:
        if not isinstance(self, DN):
            raise TypeError("this expression was not a DN.")
        for value in self.data.values():
            if not isinstance(value, SN):
                raise TypeError("a subexpression is not of type SN.")
        return self

    def is_dnon(self : Any) -> DN[ON[Any]]:
        if not isinstance(self, DN):
            raise TypeError("this expression was not a DN.")
        for value in self.data.values():
            if not isinstance(value, ON):
                raise TypeError("a subexpression is not of type SN.")
        return self