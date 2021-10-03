from flask import Blueprint,jsonify, request, Response, send_file
from flask_bcrypt import Bcrypt
from .models import Song, Comment, Response
from user.models import User
import jwt, datetime,json,random, string, os
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from datetime import datetime
import time

router = Blueprint('song', __name__)
bcrypt = Bcrypt()

def gen_id(N, w):

  
    ids_path = os.path.join(os.path.dirname(__file__), 'ids.json')
    none = None
    with open(ids_path) as f:
        obj = json.load(f)
        
        ran_id = str(''.join(random.choices(string.ascii_lowercase + string.digits, k = N)))
    if ran_id in obj[w]:
        gen_id(N, w)
    else:
        obj[w].append(ran_id)
        with open(ids_path, 'w') as f:
            json.dump(obj,f) 
        return ran_id

@router.route('/song/upload', methods=['POST'])
@jwt_required()
def upload():

    try:

        user = get_jwt_identity()
        print(user)

        if user:
            user = User.objects(email=user)[0]
            song = Song()
            for key, value in request.form.items():
                setattr(song, key, value)

            song.iid = gen_id(7, 'songs')
            song.uploader = user.iid
            song.save()
            user.songs.append(song)
            user.save()
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

def clean_data(item):

    item = json.loads(item.to_json())
    return item

@router.route('/songs', methods=['GET', 'POST'])
def songs():
    
    tracks = Song.objects()

    def clean_replies(resp):
        by = User.objects(iid=resp.by)[0].to_json()
        resp.by = json.loads(by)
        return json.loads(resp.to_json())

    def clean_comments(comment):
        commenter = User.objects(iid=comment.commenter)[0].to_json()
        comment.commenter = json.loads(commenter)
        comment.replies = list(map(clean_replies, comment.replies))
        return json.loads(comment.to_json())

    def clean_songs(song):
        uploader = User.objects(iid=song.uploader)[0].to_json()
        song.uploader = json.loads(uploader)
        song.comments = list(map(clean_comments, song.comments))

        song = song.to_json()
        return json.loads(song)

    data = list(map(clean_songs, tracks))
    try:
        #print(tracks.get())
        return jsonify({'songs': data}), 200
    except  Exception as e:
        print(e)
        return 'Exception' 



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
def comments(iid):


    try:
        action = request.args['action']
        user = get_jwt_identity()
        info = request.form
        if user:
            user = User.objects(email=user)[0]
            if action == 'reply':

                comment_id = request.args.get('comment_id')
                song = Song.objects(iid=iid)


                if song :
                    song = song[0]
                    comment = list(filter(lambda x : x['iid'] == comment_id, song.comments))
                    
                    
                    """if comment:
                        comment = comment[0]
                        
                        response = Response()
                        response.body = info['body']
                        response.iid = gen_id(7, 'responses')
                        response.commenter = user.iid
                        response.secs_since_epoch = int(time.time())
                        response.date_created = datetime.now()

                        update_dict = {
                            'set__comments__'
                        }
                        replies = comment.replies
                        replies.append(response)
                        comment.replies = replies
                        song.save()

                        commenter = json.loads(user.to_json())
                        response.commenter = commenter

                        data = response.to_json()

                        return {'data' : json.loads(data)}, 200"""
                    if comment:
                        comment = comment[0]
                        response = Response()
                        response.body = info['body']
                        response.iid = gen_id(7, 'responses')
                        response.by = user.iid
                        response.secs_since_epoch = int(time.time())
                        response.date_created = datetime.now()

                        ind = song.comments.index(comment)
                        replies = comment.replies
                        replies.append(response)
                        update_dict = {
                            f'set__comments__{ind}__replies' : replies
                        }

                        song.update(**update_dict)

                        by = json.loads(user.to_json())
                        response.by = by
                        data = response.to_json()

                        return {'data' : json.loads(data)}, 200
                    else:
                        return {'message' : 'No such comment with specified iid.'}, 404
                else:
                    return {'message' : 'No such song with specified iid.'}, 404

            elif action == 'add':


                
                comment = Comment()
                comment.body = info['body']
                comment.iid = gen_id(7, 'comments')
                comment.secs_since_epoch = int(time.time())
                comment.date_created = datetime.now()


                song = Song.objects(iid=iid)
                if not song:
                    return {'message': 'Song not found'}, 404


                
                comment.commenter = user.iid
                comment.song = iid
                song = song[0]
                song.comments.append(comment)
                song.save()
                commenter = json.loads(user.to_json())
                comment.commenter = commenter
                data = comment.to_json()

                print(data)
                return {'data': json.loads(data)}


                return {'data': 'Comment updated'}
        else:
            return {'message' : 'Not authorized to comment'} , 401
    except Exception as e:
        print(e)
        return {'message': 'Check your request body'}, 400



@router.route('/song/protected', methods=['GET'])
@jwt_required()
def protected_song():

    return {'data': 'user'}

@router.route('/comments', methods=['GET'])
def comms():

    comments = Comment.objects
    
    def clean_comments(comment):
        return comment.get()

    print()
    return {"comments" : list(map(clean_comments, comments))}