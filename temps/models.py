from mongoengine import * 

class TempPath(Document):
    user = EmailField()

    def __str__(self):
        return self.user

class TempToken(Document):
    code = IntField(unique=True, max_length=6)
    token = StringField()

    def __str__(self):
        return self.code