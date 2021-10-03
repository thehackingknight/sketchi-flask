from flask import Flask,jsonify
from mongoengine import Document, ListField, StringField, URLField, DateTimeField, ReferenceField, EmbeddedDocumentField
from datetime import datetime
from user.models import User
from .models import Song

class Comment(Document):

    commenter = ReferenceField(User)
    song = ReferenceField(Song)

    body = StringField()

    date_created = DateTimeField(
        default=datetime.utcnow()
    )
    last_modified = DateTimeField(
        default=datetime.utcnow(),
        
    )

    def __str__(self):
        return self.body[20]