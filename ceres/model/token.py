import datetime
import requests
from peewee import CharField, DateTimeField, DoesNotExist
from ceres.config import AppConfig
from .base import BaseModel


class Token(BaseModel):
    token_str = CharField()
    update_time = DateTimeField()
    expire_time = DateTimeField()

    @classmethod
    def get_token(cls):
        try:
            token = cls.get()
        except DoesNotExist:
            token = cls.fetch_from_wx_and_create()
        if token.is_expired():
            token = cls.fetch_from_wx_and_create()
        return token

    @classmethod
    def fetch_from_wx_and_create(cls):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'.format(AppConfig.WECHAT_CORP_ID, AppConfig.WECHAT_SECRET)
        r = requests.get(url)
        d = r.json()
        token_str = d['access_token']
        expires_in = d['expires_in']
        update_time = datetime.datetime.now()
        expire_time = update_time + datetime.timedelta(0, expires_in)
        return cls.create(token_str=token_str, update_time=update_time, expire_time=expire_time)

    def is_expired(self):
        return self.expire_time > datetime.datetime.now()
