import mongoengine as me

class Notifications(me.Document):

    is_read = me.BooleanField(default=False)

