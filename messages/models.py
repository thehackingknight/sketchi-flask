from mongoengine import *

class Message(Document):

    _from = DictField(required=True)
    sent = BooleanField(default=False)
    date_created = DateTimeField(required=True)
    body = StringField(required=True)
