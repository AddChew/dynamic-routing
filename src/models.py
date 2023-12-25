from tortoise import fields, models


class Users(models.Model):
    id = fields.IntField(pk = True)
    username = fields.CharField(max_length = 20, unique = True)
    hashed_password = fields.CharField(max_length = 255)


class Projects(models.Model):
    id = fields.IntField(pk = True)
    name = fields.CharField(max_length = 50)
    owner = fields.ForeignKeyField(model_name = Users, related_name = "projects")