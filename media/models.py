import mongoengine as me

class Media(me.Document):

    name = me.StringField()
    ext = me.StringField()
    _type = me.StringField()
    _file = me.FileField()

    def __str__(self):
        return str(self.id)

class Track(me.Document):

    title = me.StringField()
    genre = me.StringField()
    
    def __str__(self):
        return self.title