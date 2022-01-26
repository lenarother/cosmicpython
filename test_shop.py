from datetime import date

import pytest

from shop import Batch, OrderLine, OutOfStock, allocate
from utils import after_tomorrow, tomorrow


def test_batch_quantity_decreases_after_allocating_an_order_line():
    batch = Batch('batch-001', 'SMALL-TABLE', 20, eta=date.today())
    order_line = OrderLine('ref-123456789', 'SMALL-TABLE', 2)
    batch.allocate(order_line)
    assert batch.available_quantity == 18


def test_cannot_allocate_line_to_batch_with_smaller_quantity():
    batch = Batch('batch-001', 'BLUE-CUSHION', 1, eta=date.today())
    order_line = OrderLine('ref-123456789', 'BLUE-CUSHION', 2)
    assert batch.can_allocate(order_line) is False


def test_order_line_can_be_allocated_only_once():
    batch = Batch('batch-001', 'BLUE-VASE', 10, eta=date.today())
    order_line = OrderLine('ref-123456789', 'BLUE-VASE', 2)
    batch.allocate(order_line)
    batch.allocate(order_line)
    assert batch.available_quantity == 8


def test_deallocation_has_no_effect_without_allocation():
    batch = Batch('batch-001', 'DECORATIVE-TRINKET', 20, eta=date.today())
    order_line = OrderLine('ref-123456789', 'DECORATIVE-TRINKET', 2)
    batch.deallocate(order_line)
    assert batch.available_quantity == 20


def test_deallocation_increases_quantity_back():
    batch = Batch('batch-001', 'DECO-TRINKET', 20, eta=date.today())
    order_line = OrderLine('ref-123456789', 'DECO-TRINKET', 2)
    batch.allocate(order_line)
    assert batch.available_quantity == 18
    batch.deallocate(order_line)
    assert batch.available_quantity == 20


def test_prefer_in_stock_batches():
    batch_in_shipment = Batch('batch-001', 'DECO-TRINKET', 20, eta=date.today())
    batch_in_stock = Batch('batch-002', 'DECO-TRINKET', 20, eta=None)
    order_line = OrderLine('ref-123456789', 'DECO-TRINKET', 2)
    result_ref = allocate(order_line, [batch_in_shipment, batch_in_stock])
    assert result_ref == 'batch-002'


def test_prefer_batches_nearer_in_future():
    batches = [
        Batch('batch-001', 'DECO-TRINKET', 20, eta=tomorrow()),
        Batch('batch-002', 'DECO-TRINKET', 20, eta=date.today()),
        Batch('batch-003', 'DECO-TRINKET', 20, eta=after_tomorrow()),
    ]
    order_line = OrderLine('ref-123456789', 'DECO-TRINKET', 2)
    assert allocate(order_line, batches) == 'batch-002'


def test_raise_out_of_stock_if_cannot_allocate():
    batches = [
        Batch('batch-001', 'DECO-TRINKET', 1, eta=tomorrow()),
        Batch('batch-002', 'DECO-TRINKET', 1, eta=date.today()),
        Batch('batch-003', 'DECO-TRINKET', 1, eta=after_tomorrow()),
    ]
    order_line = OrderLine('ref-123456789', 'DECO-TRINKET', 2)
    with pytest.raises(OutOfStock):
        allocate(order_line, batches)
