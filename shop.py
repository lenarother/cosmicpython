from dataclasses import dataclass
from datetime import date
from typing import List, Optional


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:

    order_id: str
    sku: str
    quantity: int


class Batch:

    def __init__(self, ref: str, sku: str, quantity: int, eta: Optional[date]):
        self.ref = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocations = set()

    def __repr__(self):
        return f'<Batch: {self.ref}>'

    def __hash__(self):
        return hash(self.ref)

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.ref == other.ref

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def can_allocate(self, order_line: OrderLine) -> bool:
        return (
            self.sku == order_line.sku and
            self.available_quantity >= order_line.quantity
        )

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine):
        if order_line in self._allocations:
            self._allocations.remove(order_line)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self) -> int:
        return sum([i.quantity for i in self._allocations])


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(order_line))
    except StopIteration:
        raise OutOfStock('Not enough items to make a purchase.')

    batch.allocate(order_line)
    return batch.ref
