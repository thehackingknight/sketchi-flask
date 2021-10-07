
from mongoengine import Document, ListField, StringField, URLField, BooleanField, DateTimeField, ReferenceField
import json, os
from datetime import datetime
DB_URL = 'https://sketchidb.herokuapp.com' #'http://localhost:5500'
class User(Document):

    username = StringField(
        unique = True,
        required = True,
        max_length = 20
    )
    email = StringField(
        unique = True,
        required = True,
        max_length = 50
    )
    password = StringField(
        required = True,
    )
    first_name = StringField(
        max_length = 50
    )
    last_name = StringField(
        max_length = 50
    )
    bio = StringField(
        max_length = 100
    )
    iid = StringField(
        unique = True,
        max_length = 7,
        required = True
    )

    avatar = URLField(
        default = DB_URL + "/sketchi/media/images/avatardummy.jpg"
    )
    followers = ListField()    
    following = ListField()    
    playlist = ListField()    
    songs = ListField()   

    is_verified = BooleanField(
        default=False
        ) 
    is_pro = BooleanField(
        default=False
        ) 
    
    date_created = DateTimeField(
        default=datetime.utcnow()
    )
    last_modified = DateTimeField(
        default=datetime.utcnow()
    )
    def __str__(self):
        return self.username
