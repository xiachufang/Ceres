# coding: utf-8
import pytest
from peewee import IntegrityError
from ceres.model.bill import Bill


def test_create_bill(u0):
    bill = Bill.create_one(u0.id, 10)
    assert bill.payer().id == u0.id
    assert bill.amount == 10


def test_one_user_in_bill(u0):
    bill = Bill.create_one(u0.id, 10)
    users = bill.take_part_in_users()
    assert len(users) == 1
    assert users[0].id == u0.id


def test_two_users_in_bill(u0, u1):
    bill = Bill.create_one(u0.id, 10)
    with pytest.raises(IntegrityError):
        bill.add_take_part_in_user(u0)
    assert bill.average_amount() == 10
    bill.add_take_part_in_user(u1)
    users = bill.take_part_in_users()
    assert len(users) == 2
    assert users[1].id == u1.id
    assert bill.average_amount() == 10 / 2


def test_user_bills(u0, u1):
    bill1 = Bill.create_one(u0.id, 40)
    Bill.create_one(u1.id, 20)
    bill1.add_take_part_in_user(u1)
    u0_paid_bills = Bill.get_paid_by_user(u0.id)
    u1_paid_bills = Bill.get_paid_by_user(u1.id)
    assert len(u0_paid_bills) == 1
    assert len(u1_paid_bills) == 1
    u0_only_joined_bills = Bill.get_only_joined_by_user(u0.id)
    u1_only_joined_bills = Bill.get_only_joined_by_user(u1.id)
    assert len(u0_only_joined_bills) == 0
    assert len(u1_only_joined_bills) == 1


def test_delete_bill(u0, u1):
    bill1 = Bill.create_one(u0.id, 40)
    bill1.add_take_part_in_user(u1)
    bill1.delete_bill()
    u0_paid_bills = Bill.get_paid_by_user(u0.id)
    assert len(u0_paid_bills) == 0
    Bill.create_one(u0.id, 40)
    u1_only_joined_bills = Bill.get_only_joined_by_user(u1.id)
    assert len(u1_only_joined_bills) == 0
