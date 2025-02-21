from __future__ import annotations
import pytest
from pyper.nodes import SN, ON, DN
import pyper.on_dict
import pyper.on_obj
import pyper.on_seq


def test_installation():
    assert True

@pytest.mark.parametrize(
        "iterable", [
            (range(100)),
            ([0,1,2,3,4,5,6]),
            (100),
        ]
)
class TestSNInit:
    def test_safe_init(self, iterable):
        sn = SN(iterable)
        assert isinstance(sn.data, tuple) #converts to tuple