from fractions import Fraction
from dataclasses import dataclass
from typing import Generic, TypeVar, overload

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
    
@dataclass(frozen=True, init=False)
class Unit:
    name: str
    symbol: str
    dimension: Dimension
    scale: Fraction = Fraction(1)
    pi_exponent: Fraction = Fraction(0)
    offset: Fraction = Fraction(0)

    def __init__(
            self,
            name: str,
            symbol: str,
            dimension: Dimension,
            scale: Fraction | int = Fraction(1),
            pi_exponent: Fraction | int = Fraction(0),
            offset: Fraction | int = Fraction(0),
            base_unit: 'Unit | None' = None,
    ) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'symbol', symbol)
        object.__setattr__(self, 'dimension', dimension)
        object.__setattr__(self, 'scale', Fraction(scale) * (base_unit.scale if base_unit else 1))
        object.__setattr__(self, 'pi_exponent', Fraction(pi_exponent) + (base_unit.pi_exponent if base_unit else 0))
        object.__setattr__(self, 'offset', Fraction(offset) + (base_unit.offset if base_unit else 0))

    def __call__(self, value: 'float | int | Quantity') -> 'Quantity':
        if isinstance(value, Quantity):
            return value.to(self)
        return Quantity(value=value, unit=self)
    


@dataclass(frozen=True)
class Quantity(Generic[D]):
    value: float
    unit: Unit

    def to(self, target_unit: Unit) -> 'Quantity':
        if self.unit.dimension != target_unit.dimension:
            raise ValueError(f"Cannot convert from {self.unit.dimension} to {target_unit.dimension}")
        
        # Convert to base unit
        base_value = (self.value - self.unit.offset) / self.unit.scale
        
        # Convert to target unit
        target_value = base_value * target_unit.scale + target_unit.offset
        
        return Quantity(value=target_value, unit=target_unit)