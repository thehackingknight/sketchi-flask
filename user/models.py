
import mongoengine as me
import json, os
from datetime import datetime
DB_URL = os.getenv('DB_URL') if os.getenv('DB_URL') is not None else ''


class AnonymousUser(me.Document):
    ip = me.StringField(unique=True)

class User(me.Document):

    username = me.StringField(
        unique = True,
        required = True,
    )
    email = me.StringField(
        unique = True,
        required = True,
    )
    password = me.StringField(
        required = True,
    )
    first_name = me.StringField(
        max_length = 50
    )
    last_name = me.StringField(
        max_length = 50
    )
    bio = me.StringField(
        max_length = 500
    )

    address = me.StringField()
    iid = me.StringField(
        unique = True,
        required = True
    )

    avatar = me.URLField(
        default = DB_URL + "/sketchi/media/images/avatardummy.png"
    )

    facebook = me.URLField()
    twitter = me.URLField()
    youtube = me.URLField()
    followers = me.ListField()    
    following = me.ListField()    
    playlist = me.ListField()
    playlists = me.ListField(me.ReferenceField('Playlist'))  
    songs = me.ListField()
    is_admin= me.BooleanField(default=False)

    is_verified = me.BooleanField(
        default=False
        )
    is_joining = me.BooleanField(
        default=True
        )
    is_pro = me.BooleanField(
        default=False
        ) 
    
    date_created = me.DateTimeField(
        default=datetime.utcnow()
    )
    last_modified = me.DateTimeField(
        default=datetime.utcnow()
    )
    def __str__(self):
        return self.username
