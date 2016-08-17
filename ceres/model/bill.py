# coding: utf-8
import datetime
from peewee import IntegerField, FloatField, DateTimeField, DoesNotExist
from .base import BaseModel
from .user import User
from .user_in_bill import UserInBill


class Bill(BaseModel):
    payer_id = IntegerField()       # 支付者 id，参与吃饭者由另外的 user_in_bill 统计
    amount = FloatField()           # 自己支付需要报销的金额
    receipt_time = DateTimeField()  # 账单的时间
    update_time = DateTimeField()   # 更新时间

    @classmethod
    def create_one(cls, payer_id, amount, receipt_time=None):
        if not receipt_time:
            receipt_time = datetime.datetime.now()
        bill = Bill.create(payer_id=payer_id, amount=amount, receipt_time=receipt_time, update_time=datetime.datetime.now())
        bill.add_take_part_in_user(payer_id)
        return bill

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.get(id=id)
        except DoesNotExist:
            return None

    @classmethod
    def get_paid_by_user(cls, user_id, start_time=None, end_time=None):
        if not start_time and not end_time:
            _st = datetime.datetime.now()
            _en = _st + datetime.timedelta(days=1)
            start_time = datetime.datetime(_st.year, _st.month, _st.day)
            end_time = datetime.datetime(_en.year, _en.month, _en.day)
        return Bill.select().where((Bill.payer_id == user_id) & (Bill.receipt_time > start_time) & (Bill.receipt_time < end_time))

    @classmethod
    def get_only_joined_by_user(cls, user_id, start_time=None, end_time=None):
        # UserInBill 上的时间可能不对，所以这里先多做一些处理
        if not start_time and not end_time:
            _st = datetime.datetime.now()
            _en = _st + datetime.timedelta(days=1)
            start_time = datetime.datetime(_st.year, _st.month, _st.day)
            end_time = datetime.datetime(_en.year, _en.month, _en.day)
        bills = Bill.select().where((Bill.payer_id != user_id) & (Bill.receipt_time > start_time) & (Bill.receipt_time < end_time))
        return [bill for bill in bills if user_id in bill.take_part_in_user_ids()]

    def payer(self):
        return User.get_by_id(self.payer_id)

    def take_part_in_users_count(self):
        return len(UserInBill.get_by_bill(self.id))

    def take_part_in_user_ids(self):
        user_in_bills = UserInBill.get_by_bill(self.id)
        return [uib.user_id for uib in user_in_bills]

    def take_part_in_users(self):
        return User.get_by_ids(self.take_part_in_user_ids())

    def add_take_part_in_user(self, user_id):
        UserInBill.create_one(self.id, user_id)

    def average_amount(self):
        return self.amount / len(self.take_part_in_users())

    def delete_bill(self):
        UserInBill.delete_by_bill(self.id)
        self.delete_instance()
