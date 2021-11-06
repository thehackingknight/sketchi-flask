from mongoengine import * 

class Playlist(Document):
    name = StringField()
    creator = ReferenceField('User')
    date_created = DateTimeField()
    last_modified = DateTimeField()
    songs = ListField(default=[])
    state = StringField(default='private')
    description = StringField(max_length=200)
    def __str__(self):
        return self.name