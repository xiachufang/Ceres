from ceres.model.base import db
from ceres.model.user import User
from ceres.model.token import Token
from ceres.model.bill import Bill
from ceres.model.user_in_bill import UserInBill


def main():
    db.connect()
    db.create_tables([Token, User, Bill, UserInBill])


if __name__ == '__main__':
    main()
