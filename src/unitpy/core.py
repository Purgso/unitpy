from fractions import Fraction
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, overload

from .registry import REGISTRY

D = TypeVar('D')

@dataclass(frozen=True, init=False)
class Dimension:
    time: Fraction = Fraction(0)
    length: Fraction = Fraction(0)
    mass: Fraction = Fraction(0)
    angle: Fraction = Fraction(0)
    current: Fraction = Fraction(0)
    temperature: Fraction = Fraction(0)
    amount_of_substance: Fraction = Fraction(0)
    luminous_intensity: Fraction = Fraction(0)
    data: Fraction = Fraction(0)

    def __init__(
            self,
            time: Fraction | int = Fraction(0),
            length: Fraction | int = Fraction(0),
            mass: Fraction | int = Fraction(0),
            angle: Fraction | int = Fraction(0),
            current: Fraction | int = Fraction(0),
            temperature: Fraction | int = Fraction(0),
            amount_of_substance: Fraction | int = Fraction(0),
            luminous_intensity: Fraction | int = Fraction(0),
            data: Fraction | int = Fraction(0),
    ) -> None:
        
        object.__setattr__(self, 'time', Fraction(time))
        object.__setattr__(self, 'length', Fraction(length))
        object.__setattr__(self, 'mass', Fraction(mass))
        object.__setattr__(self, 'angle', Fraction(angle))
        object.__setattr__(self, 'current', Fraction(current))
        object.__setattr__(self, 'temperature', Fraction(temperature))
        object.__setattr__(self, 'amount_of_substance', Fraction(amount_of_substance))
        object.__setattr__(self, 'luminous_intensity', Fraction(luminous_intensity))
        object.__setattr__(self, 'data', Fraction(data))

    def __str__(self) -> str:
        components = []
        if self.time != 0:
            components.append(f"T^{self.time}")
        if self.length != 0:
            components.append(f"L^{self.length}")
        if self.mass != 0:
            components.append(f"M^{self.mass}")
        if self.angle != 0:
            components.append(f"A^{self.angle}")
        if self.current != 0:
            components.append(f"I^{self.current}")
        if self.temperature != 0:
            components.append(f"Θ^{self.temperature}")
        if self.amount_of_substance != 0:
            components.append(f"N^{self.amount_of_substance}")
        if self.luminous_intensity != 0:
            components.append(f"J^{self.luminous_intensity}")
        if self.data != 0:
            components.append(f"D^{self.data}")
        
        return ' * '.join(components) if components else "dimensionless"

    def __mul__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(
            time=self.time + other.time,
            length=self.length + other.length,
            mass=self.mass + other.mass,
            angle=self.angle + other.angle,
            current=self.current + other.current,
            temperature=self.temperature + other.temperature,
            amount_of_substance=self.amount_of_substance + other.amount_of_substance,
            luminous_intensity=self.luminous_intensity + other.luminous_intensity,
            data=self.data + other.data,
        )
    
    def __truediv__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(
            time=self.time - other.time,
            length=self.length - other.length,
            mass=self.mass - other.mass,
            angle=self.angle - other.angle,
            current=self.current - other.current,
            temperature=self.temperature - other.temperature,
            amount_of_substance=self.amount_of_substance - other.amount_of_substance,
            luminous_intensity=self.luminous_intensity - other.luminous_intensity,
            data=self.data - other.data,
        )
    
    def __pow__(self, power: int | Fraction) -> 'Dimension':
        return Dimension(
            time=self.time * power,
            length=self.length * power,
            mass=self.mass * power,
            angle=self.angle * power,
            current=self.current * power,
            temperature=self.temperature * power,
            amount_of_substance=self.amount_of_substance * power,
            luminous_intensity=self.luminous_intensity * power,
            data=self.data * power,
        )
    
    def is_empty(self) -> bool:
        return self == Dimension()
    
@dataclass(frozen=True, init=False)
class Unit(Generic[D]):
    name: str
    symbol: str
    dimension: Dimension
    scale: Fraction = Fraction(1)
    pi_exponent: Fraction = Fraction(0)
    offset: Fraction = Fraction(0)
    temperature_relative: bool = False

    def __init__(
            self,
            name: str,
            symbol: str,
            dimension: Dimension,
            scale: Fraction | int = Fraction(1),
            pi_exponent: Fraction | int = Fraction(0),
            offset: Fraction | int = Fraction(0),
            base_unit: 'Unit | None' = None,
            temperature_relative: bool | None = None,
            register: bool = True,

    ) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'symbol', symbol)
        object.__setattr__(self, 'dimension', dimension)
        object.__setattr__(self, 'scale', Fraction(scale) * (base_unit.scale if base_unit else 1))
        object.__setattr__(self, 'pi_exponent', Fraction(pi_exponent) + (base_unit.pi_exponent if base_unit else 0))
        object.__setattr__(self, 'offset', Fraction(offset) + (base_unit.offset if base_unit else 0))
        object.__setattr__(self, 'temperature_relative', temperature_relative if temperature_relative is not None else (base_unit.temperature_relative if base_unit else False))
        if register:
            REGISTRY.register(self)

    def __str__(self) -> str:
        return self.name

    def to_si(self, value: int | float | Fraction) -> float:
        return float(value * self.scale + self.offset)
    def from_si(self, si_value: int | float | Fraction) -> float:
        return float((si_value - self.offset) / self.scale)

    @overload
    def __call__(self, value: int | float) -> 'Quantity[D]': ...
    @overload
    def __call__(self, value: 'Quantity[D]') -> 'Quantity[D]': ...

    def __call__(self, value: 'float | int | Quantity[D]') -> 'Quantity[D]':
        if isinstance(value, Quantity):
            return value.to(self)
        return Quantity(value=value, unit=self)
    
    def __mul__(self, other: 'Unit[D]') -> 'Unit[D]':
        return REGISTRY.canonicalize(Unit(
            name=f"({self.name} * {other.name})",
            symbol=f"{self.symbol}*{other.symbol}",
            dimension=self.dimension * other.dimension,
            scale=self.scale * other.scale,
            pi_exponent=self.pi_exponent + other.pi_exponent,
            offset=0,
            temperature_relative=self.temperature_relative or other.temperature_relative
        ))
    
    def __rmul__(self, other: int | float) -> 'Quantity[D]':
        return Quantity(value=other, unit=self)
    
    def __truediv__(self, other: 'Unit[Any]') -> 'Unit[Any]':
        return REGISTRY.canonicalize(Unit(
            name=f"({self.name} / {other.name})",
            symbol=f"{self.symbol}/{other.symbol}",
            dimension=self.dimension / other.dimension,
            scale=self.scale / other.scale,
            pi_exponent=self.pi_exponent - other.pi_exponent,
            offset=0,
            temperature_relative=self.temperature_relative or other.temperature_relative
        ))
    
    def __pow__(self, power: int | Fraction) -> 'Unit[Any]':
        # TODO: decide how to handle affine units
        return REGISTRY.canonicalize(Unit(
            name=f"({self.name} ** {power})",
            symbol=f"{self.symbol}^{power}",
            dimension=self.dimension ** power,
            scale=Fraction(self.scale ** power),
            pi_exponent=self.pi_exponent * power,
            offset=0,
            temperature_relative=self.temperature_relative
        ))

@dataclass(frozen=True)
class Quantity(Generic[D]):
    value: float
    unit: Unit[D]

    @property
    def si_value(self) -> float:
        return self.unit.to_si(self.value)

    def to(self, target_unit: Unit[D]) -> 'Quantity[D]':
        if self.unit.dimension != target_unit.dimension:
            raise ValueError(f"Cannot convert from {self.unit} to {target_unit}: incompatible dimensions {self.unit.dimension} and {target_unit.dimension}")

        # Convert to target unit
        target_value = target_unit.from_si(self.unit.to_si(self.value))
        
        return Quantity(value=target_value, unit=target_unit)
    
    def __float__(self) -> float:
        if not self.unit.dimension.is_empty():
            raise TypeError(f"Cannot convert {self.unit} to float: quantity is not dimensionless")
        return float(self.unit.to_si(self.value))
    
    def __pos__(self) -> 'Quantity[D]':
        return self
    
    def __neg__(self) -> 'Quantity[D]':
        return Quantity(value=-self.value, unit=self.unit)
    
    def __add__(self, other: 'Quantity[D]') -> 'Quantity[D]':
        other_converted = other.to(self.unit)
        return Quantity(value=self.unit.from_si(self.si_value + other_converted.si_value), unit=self.unit)
    
    def __sub__(self, other: 'Quantity[D]') -> 'Quantity[D]':
        other_converted = other.to(self.unit)
        return Quantity(value=self.unit.from_si(self.si_value - other_converted.si_value), unit=self.unit)
    
    @overload
    def __mul__(self, other: 'Quantity[Any]') -> 'Quantity[Any]': ...
    @overload
    def __mul__(self, other: int | float) -> 'Quantity[D]': ...

    def __mul__(self, other: 'Quantity[Any] | int | float') -> 'Quantity[Any]':
        if isinstance(other, Quantity):
            result_unit = self.unit * other.unit
            return Quantity(value=result_unit.from_si(result_unit.to_si(self.value) * result_unit.to_si(other.value)), unit=result_unit)
        else:
            return Quantity(value=self.value * other, unit=self.unit)
    
    @overload
    def __truediv__(self, other: 'Quantity[Any]') -> 'Quantity[Any]': ...
    @overload
    def __truediv__(self, other: int | float) -> 'Quantity[D]': ...
    
    def __truediv__(self, other: 'Quantity[Any] | int | float') -> 'Quantity[Any]':
        if isinstance(other, Quantity):
            result_unit = self.unit / other.unit
            return Quantity(value=result_unit.from_si(result_unit.to_si(self.value) / result_unit.to_si(other.value)), unit=result_unit)
        else:
            return Quantity(value=self.value / other, unit=self.unit)
        
    def __rtruediv__(self, other: int | float) -> 'Quantity[Any]':
        return Quantity(value=other / self.value, unit=self.unit ** -1)
    
    @overload
    def __floordiv__(self, other: 'Quantity[Any]') -> 'Quantity[Any]': ...
    @overload
    def __floordiv__(self, other: int | float) -> 'Quantity[D]': ...

    def __floordiv__(self, other: 'Quantity[Any] | int | float') -> 'Quantity[Any]':
        if isinstance(other, Quantity):
            result_unit = self.unit / other.unit
            return Quantity(value=result_unit.from_si(result_unit.to_si(self.value) // result_unit.to_si(other.value)), unit=result_unit)
        else:
            return Quantity(value=self.value // other, unit=self.unit)
        
    def __rfloordiv__(self, other: int | float) -> 'Quantity[Any]':
        return Quantity(value=other // self.value, unit=self.unit ** -1)
    
    @overload
    def __mod__(self, other: 'Quantity[D]') -> 'Quantity[D]': ...
    @overload
    def __mod__(self, other: int | float) -> 'Quantity[D]': ...

    def __mod__(self, other: 'Quantity[D] | int | float') -> 'Quantity[D]':
        if isinstance(other, Quantity):
            other_converted = other.to(self.unit)
            return Quantity(value=self.unit.from_si(self.si_value % other_converted.si_value), unit=self.unit)
        else:
            return Quantity(value=self.value % other, unit=self.unit)
        
    def __rmod__(self, other: int | float) -> 'Quantity[D]':
        return Quantity(value=other % self.value, unit=self.unit)
    
    @overload
    def __divmod__(self, other: 'Quantity[D]') -> tuple['Quantity[Any]', 'Quantity[D]']: ...
    @overload
    def __divmod__(self, other: int | float) -> tuple['Quantity[D]', 'Quantity[D]']: ...

    def __divmod__(self, other: 'Quantity[D] | int | float') -> tuple['Quantity[Any]', 'Quantity[D]']:
        if isinstance(other, Quantity):
            other_converted = other.to(self.unit)
            quotient = Quantity(value=self.unit.from_si(self.si_value // other_converted.si_value), unit=self.unit / other_converted.unit)
            remainder = Quantity(value=self.unit.from_si(self.si_value % other_converted.si_value), unit=self.unit)
            return quotient, remainder
        else:
            quotient = Quantity(value=self.value // other, unit=self.unit)
            remainder = Quantity(value=self.value % other, unit=self.unit)
            return quotient, remainder
        
    def __rdivmod__(self, other: int | float) -> tuple['Quantity[Any]', 'Quantity[D]']:
        quotient = Quantity(value=other // self.value, unit=self.unit ** -1)
        remainder = Quantity(value=other % self.value, unit=self.unit)
        return quotient, remainder
    
    def __pow__(self, power: int | Fraction) -> 'Quantity[Any]':
        result_unit = self.unit ** power
        return Quantity(value=result_unit.from_si(result_unit.to_si(self.value) ** power), unit=result_unit)
    
    def __rpow__(self, base: int | float) -> float:
        if self.unit.dimension.is_empty():
            return base ** self.value
        else:
            raise TypeError(f"Cannot raise {base} to the power of {self}: exponent must be dimensionless")
        
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Quantity):
            return NotImplemented
        if self.unit.dimension != value.unit.dimension:
            return False
        return self.si_value == value.si_value
    
    def __lt__(self, other: 'Quantity[D]') -> bool:
        if self.unit.dimension != other.unit.dimension:
            raise TypeError(f"Cannot compare {self} and {other}: incompatible dimensions {self.unit.dimension} and {other.unit.dimension}")
        return self.si_value < other.si_value
    
    def __le__(self, other: 'Quantity[D]') -> bool:
        if self.unit.dimension != other.unit.dimension:
            raise TypeError(f"Cannot compare {self} and {other}: incompatible dimensions {self.unit.dimension} and {other.unit.dimension}")
        return self.si_value <= other.si_value
    
    def __gt__(self, other: 'Quantity[D]') -> bool:
        if self.unit.dimension != other.unit.dimension:
            raise TypeError(f"Cannot compare {self} and {other}: incompatible dimensions {self.unit.dimension} and {other.unit.dimension}")
        return self.si_value > other.si_value
    
    def __ge__(self, other: 'Quantity[D]') -> bool:
        if self.unit.dimension != other.unit.dimension:
            raise TypeError(f"Cannot compare {self} and {other}: incompatible dimensions {self.unit.dimension} and {other.unit.dimension}")
        return self.si_value >= other.si_value
    