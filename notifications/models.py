from mongoengine import *

class Notifications(Document):

    is_read = BooleanField(default=False)
    to = ListField()
    _from = StringField(required=True)
    target = StringField(required=True)
    text = StringField()
    target_element = StringField()
    _type = StringField(required=True)
    secs_since_epoch = IntField()
    date_created = DateTimeField(required=True)