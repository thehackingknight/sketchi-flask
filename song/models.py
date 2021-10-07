from flask import Flask,jsonify
import mongoengine as me
from datetime import datetime
import json

class Response(me.EmbeddedDocument):
    by = me.StringField()  
    body = me.StringField()
    iid = me.StringField()
    likes = me.ListField()
    secs_since_epoch = me.IntField()
    last_modified = me.DateTimeField(
        
    )
    def __str__(self):
        return self.body

class Comment(me.EmbeddedDocument):

    commenter = me.StringField()
    song = me.StringField()

    body = me.StringField()
    iid = me.StringField()

    replies = me.ListField(me.EmbeddedDocumentField(Response))
    likes = me.ListField()
    date_created = me.DateTimeField(
    )
    secs_since_epoch = me.IntField()
    last_modified = me.DateTimeField(
        
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

class Song(me.Document):
    
    title = me.StringField(required=True)
    genre = me.StringField()
    uploader = me.StringField()
    artist = me.StringField(max_length=20)
    description =me.StringField(max_length=100)
    iid =  me.StringField(required=True, max_length=7)
    of_type = me.StringField(max_length=10)
    likes = me.ListField()
    shares = me.ListField()
    comments = me.ListField(me.EmbeddedDocumentField(Comment))
    playlist = me.ListField()
    year = me.StringField()
    image = me.StringField(
        default= os.getenv('DB_URL') + "/sketchi/media/images/songdummy.png")
    url= me.StringField(default= os.getenv('DB_URL') + "/sketchi/media/songs/dummy")
    
    date_created = me.DateTimeField(
        default=datetime.now()
    )
    last_modified = me.DateTimeField(
        default=datetime.now(),
        
    )
    def __str__(self):
        return self.title

    

