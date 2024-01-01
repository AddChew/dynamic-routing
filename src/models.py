from tortoise import fields, models


class Users(models.Model):
    """
    User db model.
    """
    id = fields.IntField(pk = True)
    username = fields.CharField(max_length = 20, unique = True)
    hashed_password = fields.CharField(max_length = 255)

    class PydanticMeta:
        """
        Metadata for pydantic model.
        """
        exclude = ["id", "hashed_password"]


class Projects(models.Model):
    """
    Project db model.
    """
    id = fields.IntField(pk = True)
    name = fields.CharField(max_length = 50)
    owner = fields.ForeignKeyField(model_name = "models.Users", related_name = "projects")

    class PydanticMeta:
        """
        Metadata for pydantic model.
        """
        exclude = ["id"]

    class Meta:
        """
        Metadata for table.
        """
        unique_together = ("name", "owner")
