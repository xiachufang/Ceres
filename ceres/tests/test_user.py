# coding: utf-8
from ceres.model.user import User


def test_get_user():
    user = User.get_by_wx_id('clip')
    assert user.name == u'常伟佳'
