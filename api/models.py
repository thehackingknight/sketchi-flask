import mongoengine as me

class Commen(me.EmbeddedDocument):

    content = me.StringField()
    by = me.ReferenceField('Author')

class Track(me.Document):

    title = me.StringField(max_length=100)
    iid = me.StringField(max_length=10, unique=True)
    uploader = me.ReferenceField('Author')
    comments = me.ListField(me.EmbeddedDocumentField(Commen))

    def to_sjson(self):
        return {
            "title" : self.title,
            "iid" : self.iid,
            "uploader" : self.uploader
        }

    def __str__(self):
        return self.title

class Author(me.Document):

    username = me.StringField(max_length=20, unique=True)
    
    iid = me.StringField(max_length=10, unique=True)
    songs = me.ListField(me.ReferenceField('Track'))

    def __str__(self):

        return self.username