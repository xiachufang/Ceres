import os
import pytest
from peewee import create_model_tables, drop_model_tables
from ceres.model.token import Token
from ceres.model.user import User
from ceres.model.bill import Bill
from ceres.model.user_in_bill import UserInBill


assert os.environ['CERES_APP_CONFIG'] == "ceres.config.test_config"


@pytest.fixture(autouse=True)
def db(request):
    models = [Token, User, Bill, UserInBill]
    print('create tables...')
    create_model_tables(models)

    def fin():
        print('drop tables...')
        drop_model_tables(models)
    request.addfinalizer(fin)


@pytest.fixture
def u0(request):
    return User.create(name='u0', wx_id='wx0')


@pytest.fixture
def u1(request):
    return User.create(name='u1', wx_id='wx1')


@pytest.fixture
def u2(request):
    return User.create(name='u2', wx_id='wx2')
