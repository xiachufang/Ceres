from peewee import Model, SqliteDatabase
from ceres.config import AppConfig


db = SqliteDatabase(AppConfig.DB)


class BaseModel(Model):

    class Meta:
        database = db # This model uses the "people.db" database.
