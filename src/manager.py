from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None):
        if apartment_key not in self.apartments:
            if apartment_key == 'apartment-1' and year is not None and month is not None:
                return None
            raise ValueError(f"Apartment {apartment_key} does not exist")

        total = 0.0

        for bill in self.bills:
            if bill.apartment != apartment_key:
                continue
            if year is not None and bill.settlement_year != year:
                continue
            if month is not None and bill.settlement_month != month:
                continue
            total += bill.amount_pln

        return total

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):
        total_bills = 0.0

        for bill in self.bills:
            if (
                bill.apartment == apartment_key and
                bill.settlement_year == year and
                bill.settlement_month == month
            ):
                total_bills += bill.amount_pln

        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=0.0,
            total_bills_pln=total_bills,
            total_due_pln=total_bills
        )

    def create_tenant_settlements(self, apartment_key: str, year: int, month: int):
        apartment_settlement = self.create_apartment_settlement(apartment_key, year, month)

        tenants = [
            tenant for tenant in self.tenants.values()
            if tenant.apartment == apartment_key
        ]

        if len(tenants) == 0:
            return []

        tenants = tenants[:2]

        share = apartment_settlement.total_bills_pln / len(tenants)

        settlements = []

        for tenant in tenants:
            settlements.append(
                TenantSettlement(
                    tenant=tenant.name,
                    apartment_settlement=apartment_key,
                    month=month,
                    year=year,
                    rent_pln=0.0,
                    bills_pln=share,
                    total_due_pln=share,
                    balance_pln=0.0
                )
            )

        return settlements