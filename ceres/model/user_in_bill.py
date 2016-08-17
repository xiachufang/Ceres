# coding: utf-8
import datetime
from peewee import IntegerField, DateTimeField
from .base import BaseModel


class UserInBill(BaseModel):
    bill_id = IntegerField()        # 对应的账单 id
    user_id = IntegerField()        # 账单对应的参与者的 id
    create_time = DateTimeField()   # 创建时间

    class Meta:
        indexes = (
            (('bill_id', 'user_id'), True),
        )

    @classmethod
    def create_one(cls, bill_id, user_id):
        return cls.create(bill_id=bill_id, user_id=user_id, create_time=datetime.datetime.now())

    @classmethod
    def get_by_bill(cls, bill_id):
        return cls.select().where(cls.bill_id == bill_id)

    @classmethod
    def delete_by_bill(cls, bill_id):
        cls.delete().where(cls.bill_id == bill_id).execute()
