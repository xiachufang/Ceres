# coding: utf-8
import datetime
from ceres.model.token import Token


def test_token_create_and_get():
    now = datetime.datetime.now()
    expire_time = now + datetime.timedelta(0, 7200)
    Token.create(token_str='tttt', update_time=now, expire_time=expire_time)
    token = Token.get()
    print('token_str: {}, update_time: {}, expire_time: {}'.format(token.token_str, token.update_time, token.expire_time))
    assert token.token_str == 'tttt'


def test_token_auto_create():
    token = Token.get_token()
    assert token


def test_token_is_expired():
    now = datetime.datetime.now()
    update_time = now - datetime.timedelta(0, 7300)
    expire_time = update_time + datetime.timedelta(0, 7200)
    Token.create(token_str='tttt', update_time=update_time, expire_time=expire_time)
    token = Token.get()
    assert token.is_expired()
