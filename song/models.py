from flask import Flask,jsonify
from mongoengine import *
from datetime import datetime
import json, os
from bson.objectid import ObjectId
DB_URL = os.getenv('DB_URL') if os.getenv('DB_URL') is not None else ''
class Response(EmbeddedDocument):

    by = StringField()  
    body = StringField()
    iid = StringField()
    likes = ListField()
    secs_since_epoch = IntField()
    last_modified = DateTimeField(
        
    )
    def __str__(self):
        return self.body

class Comment(EmbeddedDocument):
    commenter = StringField()
    song = StringField()

    body = StringField()
    iid = StringField()

    replies = ListField(EmbeddedDocumentField(Response))
    likes = ListField()
    date_created = DateTimeField(
    )
    secs_since_epoch = IntField()
    last_modified = DateTimeField(
        
    )

    def __str__(self):
        return self.body

    def get(self):
        return {
            "commenter" : json.loads(self.commenter.to_json()),
            "body" : self.body,
            "replies" : self.replies,
            "likes" : self.likes,
            }

class Song(Document):
    
    title = StringField(required=True)
    genre = StringField()
    uploader = StringField()
    album = StringField()
    artist = StringField()
    info =StringField(max_length=200)
    iid =  StringField(required=True, max_length=7)
    of_type = StringField(max_length=10)
    likes = ListField()
    shares = ListField()
    collabos = ListField()
    tags = ListField(max_length=3)
    comments = ListField(EmbeddedDocumentField(Comment))
    playlist = ListField()
    plays = ListField(default=[])
    downloads = ListField(default=[])
    release_date = StringField()
    image = StringField(
        default= DB_URL  + "/sketchi/media/images/songdummy.png"
        
        )
    url= StringField()
    cloudinary_id= StringField()
    
    duration  = StringField(default='0')
    date_created = DateTimeField(
        default=datetime.now()
    )
    last_modified = DateTimeField(
        default=datetime.now(),
        
    )
    def __str__(self):
        return self.title

    

