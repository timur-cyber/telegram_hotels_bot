import peewee
import json

database = peewee.SqliteDatabase('database.db')


class JSONField(peewee.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class BaseTable(peewee.Model):
    class Meta:
        database = database


class UserState(BaseTable):
    """Состояние пользователя внутри сценария"""
    user_id = peewee.IntegerField()
    scenario_name = peewee.CharField()
    step_name = peewee.CharField()
    context = JSONField()


class UserInfo(BaseTable):
    """Личные настройки пользователя"""
    user_id = peewee.IntegerField()
    user_nickname = peewee.CharField()
    username = peewee.CharField(null=True)
    lang = peewee.CharField()
    currency = peewee.CharField()


database.create_tables([UserState])
database.create_tables([UserInfo])
