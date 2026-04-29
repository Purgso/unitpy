from fractions import Fraction
from typing import Any, TypeVar

from .core import Dimension, Unit

D = TypeVar('D')

class _UnitRegistry:
    def __init__(self) -> None:
        self._canonical_by_key: dict[tuple[Dimension, Fraction, Fraction, Fraction, bool], Unit[Any]] = {}

    def register(self, unit: Unit[Any]) -> None:
        key = (unit.dimension, unit.scale, unit.pi_exponent, unit.offset, unit.temperature_relative)
        self._canonical_by_key[key] = unit

    def canonicalize(self, unit: Unit[D]) -> Unit[D]:
        key = (unit.dimension, unit.scale, unit.pi_exponent, unit.offset, unit.temperature_relative)
        canonical_unit = self._canonical_by_key.get(key)
        if canonical_unit is not None:
            return canonical_unit
        return unit
    
REGISTRY = _UnitRegistry()