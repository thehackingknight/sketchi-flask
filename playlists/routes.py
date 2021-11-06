from flask import request, Blueprint
from .models import Playlist
from user.models import User
from song.models import Song
import json, jwt, os
import time
from datetime import datetime
from song.routes import songs
router = Blueprint('playlist', __name__)

def validate(request):
    token = request.headers['Authorization'].split(' ')[1]
    info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    return info

@router.route('/playlists', methods=[ 'GET'])
def playlists():
    plists = Playlist.objects()
    all_songs = songs()[0].json['songs']
    def clean(plst):
        tracks = filter(lambda song: song['iid'] in plst.songs, all_songs)
        plst.songs = list(tracks)
        return json.loads(plst.to_json())
    
    
    return {'data' : list(map(clean, plists))}

@router.post('/playlist/create')
def create():

    try:

        info = validate(request)
        creator = User.objects(email=info['sub']).first()
        if creator:
            form = request.form
            plst = Playlist()

            for key, val in form.items():
                if key != 'songs':
                    setattr(plst, key, val)

            plst.creator = creator
            iid = form['iid']
            plst.songs.append(iid)

            plst.save()
            return 'Hold up'
        else:
            return 'Unauthorized', 404
    except Exception as e:
        print(e)
        return 'something went wrong', 500
