from src.manager import Manager
from src.models import Parameters, Bill, ApartmentSettlement, TenantSettlement


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0


def test_create_apartment_settlement():
    manager = Manager(Parameters())
    apartment_key = list(manager.apartments.keys())[0]

    manager.bills.append(Bill(
        apartment=apartment_key,
        date_due='2024-01-10',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=100.0,
        type='electricity'
    ))

    manager.bills.append(Bill(
        apartment=apartment_key,
        date_due='2024-01-15',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=200.0,
        type='water'
    ))

    settlement = manager.create_apartment_settlement(apartment_key, 2024, 1)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.total_bills_pln == 300.0
    assert settlement.total_due_pln == 300.0

    empty = manager.create_apartment_settlement(apartment_key, 2024, 5)
    assert empty.total_bills_pln == 0.0


def test_create_tenant_settlements():
    manager = Manager(Parameters())

    apartment_key = list(manager.apartments.keys())[0]

    tenants = list(manager.tenants.values())
    tenants[0].apartment = apartment_key
    tenants[1].apartment = apartment_key

    manager.bills.append(Bill(
        apartment=apartment_key,
        date_due='2024-01-10',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=200.0,
        type='electricity'
    ))

    settlements = manager.create_tenant_settlements(apartment_key, 2024, 1)

    assert isinstance(settlements, list)
    assert len(settlements) >= 2

    for s in settlements:
        assert isinstance(s, TenantSettlement)
        assert s.apartment_settlement == apartment_key
        assert s.month == 1
        assert s.year == 2024
        assert s.bills_pln == 100.0
        assert s.total_due_pln == 100.0

    settlements_single = manager.create_tenant_settlements(apartment_key, 2024, 2)
    assert isinstance(settlements_single, list)

    for t in manager.tenants.values():
        t.apartment = "other"

    settlements_empty = manager.create_tenant_settlements(apartment_key, 2024, 1)
    assert settlements_empty == []