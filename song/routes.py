from flask import Blueprint,jsonify, request, Response, send_file
from flask_bcrypt import Bcrypt
from .models import Song, Comment, Response
from user.models import User
from notifications.models import Notifications
import jwt, datetime,json,random, string, os
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from datetime import datetime
import time
import uuid
from media.models import Media
from io import BytesIO
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import create_access_token
import requests

router = Blueprint('song', __name__)
bcrypt = Bcrypt()
def validate(request):
    token = request.headers['Authorization'].split(' ')[1]
    info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    return info
    
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

        email = validate(request)['sub']
        files = request.files
        if email:
            user = User.objects(email=email).first()
        else:
            return {'message': 'Invalid token'}, 401

        if user:

            if not user.is_pro and len(user.songs) >= 10:
                return {'message' : 'Max number of uploads [10] reached. Upgrade to pro to upload more!'}, 400
            
            else:
                try:

                    song = Song()
                    form = request.form
                    for key, value in form.items():
                        if key != 'collabos' and key != 'tags':
                            setattr(song, key, value)
                    if 'collabos' in form:
                        song.collabos = json.loads(form['collabos'])

                    if 'tags' in form:
                        song.tags = json.loads(form['tags'])

                    song.iid = gen_id(7, 'songs')
                    song.uploader = user.iid

                    if 'image' in files:
                        img = files["image"]
                        ext = img.filename.split('.')[-1]
                        image = Media()
                        image.name = 'sketchi_' + uuid.uuid4().hex + '.' + ext
                        image._type = "image"
                        image.ext = ext
                        image._file.put(img, content_type=img.mimetype)
                        image.save()

                        song.image = os.getenv('DB_URL') + '/media/images/' + image.name
                    if 'audio' in files:
                        aud = files["audio"]
                        track = Media()
                        track.name = 'sketchi_' + uuid.uuid4().hex
                        track._type = "audio"
                        track._file.put(aud)
                        #track._file.put(aud, content_type=aud.mimetype)
                        track.save()

                        song.url = os.getenv('DB_URL') + '/media/songs/' + str(track.id)

                    song.save()
                    try:
                        user.songs.append(song.iid)
                        user.save()
                    except Exception as e:
                        print('Dem not save')
                        print(e)
                    return jsonify({'iid' : song.iid})
                except Exception as e:
                    print(e)

                    return {"message" : "Something went wrong"}, 500

    except Exception as e:
        print(e)
        return {"message" : "Something went wrong"}, 500
        if e == 'Signature has expired':
            return {"message" : 'Token expired'}, 401
    #print(request.form)"""



def clean_data(item):

    item = json.loads(item.to_json())
    return item

@router.route('/songs', methods=['GET', 'POST'])
def songs():
    
    args = request.args
    tracks = Song.objects()
    if 'ids' in args:
        try:
            ids = json.loads(args['ids'])
            tracks = Song.objects(iid__nin=ids)[0 : 10]
        except Exception as e:
            print(e)
            return 'Something went wrong', 500
        
    if 'by' in args:
        tracks = Song.objects(uploader=args['by'])

    if 'rt' in args:
        song = Song.objects(iid=args['rt']).first()
        filters = Q(uploader=song.uploader)
        filters  | Q(album=song.album) if song.album else ''
        tracks = Song.objects(filters)
    #else:
    #return {'message': 'Please provide list of IDS'}, 400


    params = request.args
    if 'genre' in params:
        genre = params['genre']
        tracks = Song.objects(genre = genre)
        if genre == 'all':
            tracks = Song.objects()
    if 'iid' in params:
        iid = params['iid']
        tracks = Song.objects(iid = iid)
        if not len(tracks):
            return 'Song not found', 404


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
        song.url = create_access_token(identity={'url': song.url})
        song = song.to_json()
        
        return json.loads(song)

    data = list(map(clean_songs, tracks))
    try:
        #print(tracks.get())
        return {'songs': data}, 200
    except  Exception as e:
        print(e)
        return 'Exception' , 500



@router.route('/songs/suggested', methods=['GET', 'POST'])
def suggested():
    
    args = request.args
    tracks = Song.objects()
    if 'ids' in args:
        try:
            ids = json.loads(args['ids'])
            tracks = Song.objects(iid__nin=ids)[0 : 10]
        except Exception as e:
            print(e)
            return 'Something went wrong', 500
        
    if 'by' in args:
        tracks = Song.objects(uploader=args['by'])

    if 'rt' in args:
        song = Song.objects(iid=args['rt']).first()
        filters = Q(uploader=song.uploader)
        filters  | Q(album=song.album) if song.album else ''
        tracks = Song.objects(filters)
    #else:
    #return {'message': 'Please provide list of IDS'}, 400


    params = request.args
    if 'genre' in params:
        genre = params['genre']
        tracks = Song.objects(genre = genre)
        if genre == 'all':
            tracks = Song.objects()
    if 'iid' in params:
        iid = params['iid']
        tracks = Song.objects(iid = iid)
        if not len(tracks):
            return 'Song not found', 404


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
        song.url = create_access_token(identity={'url': song.url})
        song = song.to_json()
        
        return json.loads(song)

    data = list(map(clean_songs, tracks))
    try:
        #print(tracks.get())
        return {'songs': data}, 200
    except  Exception as e:
        print(e)
        return 'Exception' , 500




@router.route('/song/<iid>', methods=['GET'])
def song_by_iid(iid):
    try:
        track = Song.objects(iid=iid).first()
        if track:
            track = track.to_json()
            """
            uploader = User.objects(iid = track['uploader_id'])[0]
            uploader = uploader._data
            del uploader['password']
            del uploader['id']
            track['uploader'] = uploader"""
            
            return jsonify({'song': json.loads(track)})
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
            return send_file(filepath, download_name=filename)
        with open(filepath, 'rb') as f:

            return f.read()#send_file(filepath, attachment_filename='file', as_attachment=False)
    except Exception as e:
        print(e)
        return {'message': 'Could not find file specified'}, 404

@router.route('/song/<iid>/download', methods=['POST'])
def download(iid):
    song = Song.objects(iid=iid).first()
    if song:
        if 'dldtkn' in request.args:
            token = request.args['dldtkn']
            info = jwt.decode(token, 'CyuJT65KcLcNSOUJVLNCqXztE4XNYkG5', algorithms=['HS256'])
            ip = info['ip']
            song.downloads.append(ip)
            song.save()

            return 'OK'

        else:
            return 'Missing Token', 400

@router.route('/song/<iid>/update', methods=['POST'])
@jwt_required()
def update_song(iid):
    feature = request.args['f']
    song = Song.objects(iid=iid).first()
    email = validate(request)['sub']
    
    files = request.files
    form = request.form
    if email:
        
        user = User.objects(email=email).first()
    else:
        return {'message' : 'Invalid token'}, 401

    if feature == 'info':

        
        for key, value in form.items():

            if key != 'collabos' and key != 'tags':
                setattr(song, key, value)
                song.collabos = json.loads(form['collabos'])
                song.tags = json.loads(form['tags'])

            if key == 'comments':
                comments = json.loads(value)
                song.comments = comments

        if 'image' in files:
            #Delete prev image
            image = None
            try:
                image = Media.objects(name=song.image.split('/')[-1]).first()
            except Exception as e:
                pass
            if image:
                image.delete()
                print('Song Prev Image deleted')
            img = files["image"]
            ext = img.filename.split('.')[-1]
            image = Media()
            image.name = 'sketchi_' + uuid.uuid4().hex + '.' + ext
            image.ext = ext
            image._type = "image"
            image._file.put(img, content_type=img.mimetype)
            image.save()
            song.image = os.getenv('DB_URL') + '/media/images/' + image.name
        song.save()




    #song = song_by_iid(iid).json
    return 'song'


@router.route('/song/<iid>/like', methods=['POST'])
@jwt_required()
def like(iid):

    try:

        email = validate(request)['sub']
        action = request.args['act']
        if email:
            user = User.objects(email=email).first()
            song = Song.objects(iid=iid).first()

            if action == 'like':
                if user.iid not in song.likes:
                    song.likes.append(user.iid)
                    
                    print('saving song')
                    song.save()
                    return {'data': 'Song liked'}, 200

                else:
                    return 'User already liked the song', 400

            elif action== 'dislike':
                song.likes.remove(user.iid)
                song.save()

                return {'data': 'Song disliked'}, 200
        else:
            return {'message' : 'User not logged'}, 401

    except Exception as e:
        print(e)
        return 'Som went wrong', 500

@router.route('/song/<iid>/delete', methods=['POST'])
@jwt_required()
def delete_song(iid):
    try:
        email = validate(request)['sub']
        if email:
            user = User.objects(email=email).first()
        else:

            return {'message' : 'Invalid token'}, 401
        if user:
            song = Song.objects(iid=iid).first()

            if song:
                user.songs.remove(iid)
                song.delete()
                user.save()
                return 'Song deleted successfully', 200
            else:
                return {'message' : "Something went wrong"}, 500

    except Exception as e:
        print(e)
        return {'message' : "Something went wrong"}, 500
            
@router.route('/song/<iid>/comment', methods=['POST'])
@jwt_required()
def comments(iid):


    try:
        action = request.args['action']
        email = validate(request)['sub']
        if email:
            user = User.objects(email=email).first()
        else:
            return {'message' : 'Not authenticated'}, 401
        info = request.form
        if user:
            
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
                        response.iid = gen_id(7, 'responses')
                        response.body = info['body']
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
                comment.iid = gen_id(7, 'comments')
                comment.body = info['body']
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



@router.route('/search', methods=['GET'])
def search():

    params = request.args

    if 'q' in params:
        q = params['q']

        songs = []
        for song in Song.objects(title__icontains=q):
            songs.append(song)
        for song in Song.objects(info__icontains=q):
            songs.append(song)
        artists = []
        for a in User.objects(username__icontains=q):
            artists.append(a)
        for a in User.objects(bio__icontains=q):
            artists.append(a)
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

        def clean_users(user):

            user = user.to_json()
            return json.loads(user)

        artsts = list(map(clean_users, artists))

        sngs = list(map(clean_songs, songs))
        return {'songs' : sngs, 'artists' : artsts}


@router.post('/song/<song_id>/play')
def play(song_id):

    user = 'anonymous'
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(' ')[1]
        if token:
            email = validate(request)['sub']
            user = User.objects(email = email).first()
    
    song = Song.objects(iid=song_id).first()
    if song:
        song.plays.append('anonymous') if user == 'anonymous' else song.plays.append(str(user.id)) 
        song.save()
        return {'plays' : len(song.plays)}

    else:
        return 'song not found', 404

@router.get('/file')
def get_blob():
    params = request.args

    if 'url' in params:
        
        token = params['url']
        info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        
        url = info['sub']['url']
        res =requests.get(url)

        return res.text
    else:
        return '', 400