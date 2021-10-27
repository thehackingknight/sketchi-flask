from mongoengine import * 

class TempPath(Document):
    user = EmailField()

    def __str__(self):
        return self.user