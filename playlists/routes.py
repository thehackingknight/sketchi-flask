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
    all_songs = songs()[0]['songs']
    
    
    if 'creator' in request.args:
        c = request.args['creator']
        plists = Playlist.objects(creator=c)
    def clean(plst):
        tracks = filter(lambda song: song['iid'] in plst.songs, all_songs)
        plst.songs = list(tracks)
        return json.loads(plst.to_json())

    return {'data' : list(map(clean, plists))}
@router.get('/playlist/<oid>')
def plist(oid):
    p = Playlist.objects(pk=oid).first()
    all_songs = songs()[0]['songs']
    if p:
        tracks = filter(lambda song: song['iid'] in p.songs, all_songs)
        p.songs = list(tracks)
        return {'playlist': json.loads(p.to_json())}
    else:
        return '', 404
    
    return 'Hold up'
@router.post('/playlist/<oid>/add')
def add(oid):
    plst = Playlist.objects(pk=oid).first()
    form = request.form
    if 'song_id' in form:
        song_id = form['song_id']
        plst.songs.remove(song_id) if song_id in plst.songs else plst.songs.append(song_id)
        plst.save()
        return {'songs' : plst.songs}, 200
    else:
        return 'no song_id specified', 400
    print(form['song_id'])
    return 'Hold up'


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
            creator.playlists.append(plst.id)
            creator.save()
            return 'Hold up'
        else:
            return 'Unauthorized', 404
    except Exception as e:
        print(e)
        if e == 'Signature has expired':
            return 'Your session has expired', 401
        return 'something went wrong', 500
