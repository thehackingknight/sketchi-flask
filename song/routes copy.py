from flask import Blueprint,jsonify, request, Response, send_file
from flask_bcrypt import Bcrypt
from .models import Song
from user.models import User
import jwt, datetime,json,random, string, os
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from datetime import datetime
import time

router = Blueprint('song', __name__)
bcrypt = Bcrypt()

def gen_id(N):

    ids_path = os.path.join(os.path.dirname(__file__), 'ids.json')
    none = None
    with open(ids_path) as f:
        songs = json.load(f)['songs']
        
        ran_id = str(''.join(random.choices(string.ascii_lowercase + string.digits, k = N)))
    if ran_id in songs:
        gen_id(N)
    else:
        songs.append(ran_id)
        with open(ids_path, 'w') as f:
            json.dump({"songs" : songs},f) 
        return ran_id

@router.route('/song/upload', methods=['POST'])
def upload():

    try:
        song = Song()
        for key, value in request.form.items():
            setattr(song, key, value)

        song.iid = gen_id(7)
        uploader = User.objects(iid = song.uploader_id)[0]

        song.save()
        uploader.songs.append(song)
        uploader.save()
        return jsonify({'songId' : song.iid})

    except Exception as e:
        print(e)
        return Response(
                response="Something went wrong",
                status=500
            )
        if e == 'Signature has expired':
            return Response(
                response="Token expired",
                status=400
            )
    #print(request.form)"""

@router.route('/songs', methods=['GET', 'POST'])
def songs():

    data = Song.objects()
    final_data = []
    
    for song in data:
        song = song._data
        del song['id']

        uploader = User.objects(iid = song['uploader_id'])
        comments = Comment.objects(song=song['iid'])
        
        #song['comments'] = comments
        if comments:

            def clean_data(comment):
                com = comment._data
                com['id']= str(com['id'])
                user_id = com['commenter']
                user = User.objects(id=user_id)
                if user:
                    user = user[0]._data
                    del user['id']
                    """user['id']= str(user['id'])
"""
                    com['commenter'] = user
                return com

            try:
                res = map(clean_data, comments)
            except Exception as e:
                print('Map yak nyisa mfan')
                print(e)
            song['comments'] = list(res)
                
        if uploader:
            uploader = uploader[0]
            uploader = uploader._data
            del uploader['password']
            del uploader['id']

            song['uploader'] = uploader
        final_data.append(song)
    return jsonify({'songs': final_data})



@router.route('/song/<iid>', methods=['GET'])
def song(iid):
    try:
        track = Song.objects(iid=iid)
        if track:
            track = track[0]._data
            del track['id']
            """
            uploader = User.objects(iid = track['uploader_id'])[0]
            uploader = uploader._data
            del uploader['password']
            del uploader['id']
            track['uploader'] = uploader"""
            
            return jsonify({'song': track})
        else:
            return {'message': 'Song not found'}, 404
    except Exception as e:
        print(e)
        return {'message': e}, 500

@router.route('/sketchi/media/<folder>/<filename>', methods=['GET'])
def media(folder, filename):

    try:
        if folder == 'songs':
            filepath = 'sketchi/media/songs/' + filename
        elif folder == 'images':
            filepath = 'sketchi/media/images/' + filename
        print(filepath)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        print(e)
        return {'message': 'Could not find file specified'}, 404


@router.route('/song/<iid>/update', methods=['POST'])
def update_song(iid):
    feature = request.args['f']
    song = Song.objects(iid=iid)[0]
    print()
    if feature == 'info':

        
        for key, value in request.form.items():

            setattr(song, key, value)
            if key == 'comments':
                comments = json.loads(value)
                song.comments = comments
        song.save()


    print()
    return {'data': 'Song updated'}



@router.route('/song/<iid>/comment', methods=['POST'])
@jwt_required()
def add_comment(iid):


    try:
        action = request.args['action']

        if action == 'reply':

            comment_id = request.args.get('comment_id')
            song = Song.objects(iid=iid)
            comment = Comment.objects(id=comment_id)
            
            if song and comment:
                song = song[0]
                comment = comment[0]
                print(comment.song)
            return 'replying to a comment'

        info = request.form
        comment = Comment()
        comment.body = info['body']
        comment.secs_since_epoch = int(time.time())
        comment.date_created = datetime.now()
        user = get_jwt_identity()

        song_exists = Song.objects(iid=iid)
        if not song_exists:
            return {'Message': 'Song not found'}, 404
        if user:
            
            user = User.objects(email=user)[0]
            comment.commenter = user['id']
            comment.song = iid
            comment.save()
            
            comment['id'] = str(comment['id'])
            
            #del user['password']
            print(comment._data)
            user['id'] = str(user['id'])
            
            comment['commenter'] = user._data
            
            return {'data': comment._data}

        else:
            return {'message': 'You are not allowed to comment!!'}, 400
        return {'data': 'Comment updated'}
    except Exception as e:
        print(e)
        return {'message': 'Check your request body'}, 400



@router.route('/song/protected', methods=['GET'])
@jwt_required()
def protected_song():

    return {'data': 'user'}