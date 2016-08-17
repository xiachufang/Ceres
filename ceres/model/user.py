import requests
from peewee import CharField, DoesNotExist
from .base import BaseModel
from .token import Token


class User(BaseModel):
    name = CharField()
    wx_id = CharField()

    @classmethod
    def get_by_id(cls, id):
        return cls.get(id=id)

    @classmethod
    def get_by_ids(cls, ids):
        return [cls.get_by_id(id) for id in ids]

    @classmethod
    def get_by_wx_id(cls, wx_id):
        try:
            user = cls.get(wx_id=wx_id)
        except DoesNotExist:
            user = cls.fetch_from_wx_and_create(wx_id)
        return user

    @classmethod
    def fetch_from_wx_and_create(cls, wx_id):
        token = Token.get_token()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={}&userid={}'.format(token.token_str, wx_id)
        r = requests.get(url)
        d = r.json()
        name = d['name']
        wx_id = d['userid']
        return cls.create(name=name, wx_id=wx_id)
