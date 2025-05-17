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

def test_create_and_get_address(db_session, test_user):
    address = Address(
        user_id=test_user.id,
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
    assert fetched.street == "Main St"

def test_get_addresses_by_user_id(db_session, test_user):
    address1 = Address(user_id=test_user.id, street="A", city="B", state="C", zip_code="111", country="X")
    address2 = Address(user_id=test_user.id, street="D", city="E", state="F", zip_code="222", country="Y")
    create_address(db_session, address1)
    create_address(db_session, address2)
    addresses = get_addresses_by_user_id(db_session, test_user.id)
    assert len(addresses) == 2

def test_update_address_by_id(db_session, test_user):
    address = Address(user_id=test_user.id, street="Old", city="City", state="ST", zip_code="000", country="Country")
    created = create_address(db_session, address)
    update_address_by_id(db_session, created.id, {"street": "New"})
    updated = get_address_by_id(db_session, created.id)
    assert updated.street == "New"

def test_delete_address(db_session, test_user):
    address = Address(user_id=test_user.id, street="Del", city="City", state="ST", zip_code="999", country="Country")
    created = create_address(db_session, address)
    deleted = delete_address(db_session, created.id)
    assert deleted is not None
    assert get_address_by_id(db_session, created.id) is None

def test_count_addresses_for_user(db_session, test_user):
    for i in range(3):
        address = Address(user_id=test_user.id, street=f"S{i}", city="C", state="S", zip_code="Z", country="P")
        create_address(db_session, address)
    count = count_addresses_for_user(db_session, test_user.id)
    assert count == 3

def test_address_exists_for_user(db_session, test_user):
    address = Address(user_id=test_user.id, street="Exist", city="C", state="S", zip_code="Z", country="P")
    create_address(db_session, address)
    class Dummy:
        street = "Exist"
        city = "C"
        state = "S"
        zip_code = "Z"
        country = "P"
    exists = address_exists_for_user(db_session, test_user.id, Dummy)
    assert exists is True
    class Dummy2:
        street = "Nope"
        city = "C"
        state = "S"
        zip_code = "Z"
        country = "P"
    not_exists = address_exists_for_user(db_session, test_user.id, Dummy2)
    assert not_exists is False

def test_update_nonexistent_address(db_session):
    updated = update_address_by_id(db_session, 9999, {"street": "No existe"})
    assert updated is None

def test_delete_nonexistent_address(db_session):
    deleted = delete_address(db_session, 9999)
    assert deleted is None

def test_get_nonexistent_address(db_session):
    address = get_address_by_id(db_session, 8888)
    assert address is None

def test_count_addresses_for_nonexistent_user(db_session):
    count = count_addresses_for_user(db_session, 12345)
    assert count == 0

def test_address_exists_for_user_with_invalid_data(db_session, test_user):
    address = Address(user_id=test_user.id, street="Valid", city="C", state="S", zip_code="Z", country="P")
    create_address(db_session, address)
    class DummyInvalid:
        street = "Other"
        city = "C"
        state = "S"
        zip_code = "Z"
        country = "P"
    exists = address_exists_for_user(db_session, test_user.id, DummyInvalid)
    assert exists is False