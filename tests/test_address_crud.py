from app.models.address_model import Address
from app.crud.address_crud import (
    create_address,
    get_address_by_id,
    get_addresses_by_user_id,
    update_address_by_id,
    delete_address,
    count_addresses_for_user,
    address_exists_for_user,
)

def test_create_and_get_address(db_session):
    address = Address(
        user_id=1,
        street="Main St",
        city="City",
        state="ST",
        zip_code="12345",
        country="Country"
    )
    created = create_address(db_session, address)
    assert created.id is not None
    fetched = get_address_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.street == "Main St"

def test_get_addresses_by_user_id(db_session):
    address1 = Address(user_id=2, street="A", city="B", state="C", zip_code="111", country="X")
    address2 = Address(user_id=2, street="D", city="E", state="F", zip_code="222", country="Y")
    create_address(db_session, address1)
    create_address(db_session, address2)
    addresses = get_addresses_by_user_id(db_session, 2)
    assert len(addresses) == 2

def test_update_address_by_id(db_session):
    address = Address(user_id=3, street="Old", city="City", state="ST", zip_code="000", country="Country")
    created = create_address(db_session, address)
    update_address_by_id(db_session, created.id, {"street": "New"})
    updated = get_address_by_id(db_session, created.id)
    assert updated.street == "New"

def test_delete_address(db_session):
    address = Address(user_id=4, street="Del", city="City", state="ST", zip_code="999", country="Country")
    created = create_address(db_session, address)
    deleted = delete_address(db_session, created.id)
    assert deleted is not None
    assert get_address_by_id(db_session, created.id) is None

def test_count_addresses_for_user(db_session):
    user_id = 5
    for i in range(3):
        address = Address(user_id=user_id, street=f"S{i}", city="C", state="S", zip_code="Z", country="P")
        create_address(db_session, address)
    count = count_addresses_for_user(db_session, user_id)
    assert count == 3

def test_address_exists_for_user(db_session):
    user_id = 6
    address = Address(user_id=user_id, street="Exist", city="C", state="S", zip_code="Z", country="P")
    create_address(db_session, address)
    class Dummy:  # Simula un schema con los mismos campos
        street = "Exist"
        city = "C"
        state = "S"
        zip_code = "Z"
        country = "P"
    exists = address_exists_for_user(db_session, user_id, Dummy)
    assert exists is True
    class Dummy2:
        street = "Nope"
        city = "C"
        state = "S"
        zip_code = "Z"
        country = "P"
    not_exists = address_exists_for_user(db_session, user_id, Dummy2)
    assert not_exists is False