
from flask import Flask,jsonify, request, Response, Blueprint

from user.models import User
from song.models import Song
import song.routes as song_routes
import jwt, datetime,json,random, string
from dotenv import load_dotenv
import os, cloudinary,json, requests, re
import cloudinary.uploader
from flask_bcrypt import Bcrypt
from random import *
from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required, verify_jwt_in_request
router = Blueprint('user', __name__)
bcrypt = Bcrypt()

load_dotenv()

mail = Mail()


def send_email(subject, message, recipients, res=None):
    msg = Message(
    subject= subject,
    sender="clickbait4587@gmail.com",
    recipients=recipients)
    
    msg.html = message
    try:
        mail.send(msg)
        return {"message" :'Email sent successfully'} if res is None else res
    except Exception as e:
        
        if res:
            # delete created users
            try:
                usr = User.objects(email=res['user']['email'])
                if usr:
                    usr = usr[0]
                    usr.delete()
                    print('User deleted')
            except Exception as e:
                print('Could not delete user')
                print(e)
        print('Could not send email Exception')        
        print(e)
        return {"message" : "Could not send email"}, 401

@router.route('/sendmail', methods=['GET'])
def sendmail():
    return send_email(
        'Testing from anoher view',
        '<h2>Let\'s get it</h2>',
        ['therealhackingknight@gmail.com'])

def get_songs(uploader_id):
    
    data = []
    songs = Song.objects(uploader_id=uploader_id)
    for song in songs:
        song = song._data
        song['id'] = str(song['id'])
        uploader = User.objects(iid=uploader_id)
        if uploader:
            uploader = uploader[0]._data
            uploader['id'] = str(uploader['id'])
            del uploader['password']
            
            song['uploader'] = uploader

        comments = Comment.objects(song=song['iid'])
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
                song['comments'] = list(res)
            except Exception as e:
                print('Map yak nyisa mfan')
                print(e)

        data.append(song)
    return data


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return True if re.match(regex, email) else False
 
# Configure cloudinary
cloudinary.config(cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'), 
    api_secret=os.getenv('CLOUDINARY_API_SECRET'))
def gen_id(N):

    ids_path = os.path.join(os.path.dirname(__file__), 'ids.json')
    none = None
    with open(ids_path) as f:
        users = json.load(f)['users']
        
        ran_id = str(''.join(choices(string.ascii_lowercase + string.digits, k = N)))
    if ran_id in users:
        gen_id(N)
    else:
        users.append(ran_id)
        with open(ids_path, 'w') as f:
            json.dump({"users" : users},f) 
        return ran_id

def gen_pass():
    
    characters = string.ascii_letters + string.punctuation  + string.digits
    password =  "".join(choice(characters) for x in range(randint(8, 16)))
    return password

def gen_token(identity, hours=1):
    return create_access_token(identity=identity)

@router.route('/users', methods=['GET'])
def users():

    users = User.objects()
    
    def clean_users(user):

        user = user.to_json()
        return json.loads(user)

    data = list(map(clean_users, users))
    #print(data)

    return {'users': data}
    

@router.route('/auth/signup', methods=['POST'])
def signup():

    method = request.args['method']
    iid = gen_id(7)
    username = request.form.get('username')
    
    email = request.form.get('email')
    password = request.form.get('password')

    existing_email = User.objects(email=email)

    if method == 'google':
        username = iid
        password = gen_pass()

        if existing_email:
            #login user
            user = User.objects(email=email)
            if user:
                user = user[0]._data
                del user['password']
                user['id'] = str(user['id'])
                token = gen_token(email)

                songs = get_songs(user)
                return {'user': user, 'token': token}
    
    
    hashed_pass = bcrypt.generate_password_hash(password)
    existing_username = User.objects(username=username)
    if existing_username:
        return {'message' : f'User with username {username} already exists!'}, 400
    if existing_email:
        return {'message' : f'User with email {email} already exists!'}, 400
    user = User()
    for key, value in request.form.items():
        setattr(user, key, value)
    if not validate_email(email):
        return {'message' : f'Please enter a valid email address.'}, 400
    user.password = hashed_pass.decode()
    user.iid = iid
    user.username = username
    try:   
               
        token = gen_token(email, 48)
        user.save()
        user = user._data
        user['id'] = str(user['id'])
        del user['password']
        url = f'{os.getenv("CLIENT_URL")}/auth/confirm?token={token}'
        
        return send_email(
            subject= "Sketchi validation email",
             message = f"""
             <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style type="text/css">


            .sketchi{{
                font-family: Poppins, Roboto,Helvetica Neue,sans-serif !important;
                text-align: center;width: 80%;
                margin: auto;
                padding: 10px;
                color: black;
               
            }}

            .sketchi *, .sketchi{{-ms-overflow-style: none;scrollbar-width: none;
            }}

            .sketchi::-webkit-scrollbar{{ display: none;}}
               
              

            .btn {{
                display: inline-block;
                font-weight: 400;
                line-height: 1.5;
                color: #212529 !important;
                text-align: center !important;
                text-decoration: none;
                vertical-align: middle;
                cursor: pointer;
                -webkit-user-select: none;
                -moz-user-select: none;
                user-select: none;
                background-color: transparent;
                border: 1px solid transparent;
                padding: .375rem .75rem;
                font-size: 1rem;
                border-radius: .25rem;
                transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;
            }}
            .btn-primary {{
                color: #fff;
                background-color: #0d6efd;
                border-color: #0d6efd;
                
            }}
    </style>
</head>
<body>

    <div class="sketchi">

    <h1>Thank you for signing up to Sketchi!</h1>

    <p>Click the button to verify your account.</p>
    <a href="{url}" target="_blank" class="btn btn-primary">Verify</a>
    
    <p>If button did not work use this link.</p>
    <a href="{url}" target="_blank">{url}</a>

    <h3>The verification is valid for only 48hrs</h3>

    <p>For support please contact us at <a href="mailto:clickbait4587@gmail.com">clickbait4587@gmail.com</a></p>
    </div>
    
</body>
</html>
             """ ,
              recipients=[email],
               res={"token": token, 'user' : user})
        
    except Exception as e:
        print(e)
        return Response(
            response= 'Something went wrong!',
            status= 500,
        )

@router.route('/auth/login', methods=['POST'])

def login():
    
    try:
        verify_jwt_in_request()
        token = request.headers['Authorization'].split(' ')[1]
        if token:
            data = get_jwt_identity()
            user = User.objects(email = data)
            if user:
                user = user[0]
                
            """
            user['_id'] = str(user['_id'])
            del user['password']"""
            return jsonify({'user' : user.to_json(), 'token': token})
    except Exception as e:
        print(e)

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.objects(email = email)
    
    if user:

        user = user[0]
        password_correct = bcrypt.check_password_hash(bytes(user.password, encoding='utf-8'), password)
        if password_correct:
            token = gen_token(email)
            
            user = user.to_json()
            return jsonify({'user' : json.loads(user), 'token' : token})
        else:
            return {"message" : "Incorrect Password"}, 400
    else:
        return {"message" : "User does not exist"}, 400

    return email
    


@router.route('/user/<iid>', methods=['GET', 'POST'])
def user(iid):

    user = User.objects(iid = iid).first()
    print(iid)
    if request.method == 'GET':

        if user:
            feature = request.args['f']

            if feature == 'playlist':
                verify_jwt_in_request()
                email = get_jwt_identity()
                if email:
                    user = User.objects(email=email).first()
                    songs = []
                    for song_id in user.playlist:
                        song = Song.objects(iid=song_id).first()
                        songs.append(song)
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
                    data = list(map(clean_songs, songs))
                    try:
                        #print(tracks.get())
                        return jsonify({'songs': data}), 200
                    except  Exception as e:
                        print(e)
                        return 'Exception'                 
                    return 'Yima nyana'
                else:
                    return 'Auth required', 401


            songs = song_routes.songs()[0].json['songs']
            #songs = json.loads(songs)

            user_songs = filter(lambda song: song['iid'] in user.songs, songs)
            user.songs = list(user_songs)
            user = user.to_json()

            return {'user' : json.loads(user)}

        else:
            return {'message' : 'No such user'}, 404
    else:

        try:

            feature = request.args['f']

            if feature == 'playlist':
                verify_jwt_in_request()
                email = get_jwt_identity()

                if email:
                    user = User.objects(email=email).first()
                    songs = []
                    for song_id in user.playlist:
                        song = Song.objects(iid=song_id).first()
                        songs.append(song)

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

                    data = list(map(clean_songs, songs))
                    try:
                        #print(tracks.get())
                        return jsonify({'songs': data}), 200
                    except  Exception as e:
                        print(e)
                        return 'Exception'                 


                    return 'Yima nyana'
                else:
                    return 'Auth required', 401


            if user:
                user = user[0]._data
                del user['id']
                songs = get_songs(iid)
                user['songs'] = songs
                del user['password']
                return jsonify({'user' : user})
            else:
                return {'message' : "User with those credentials not found."}, 404

        except Exception as e:
            print(e)
            return {"message" : 'Something went wrong!'}, 500

@router.route('/user/<iid>/update', methods=['GET', 'POST'])
@jwt_required()
def update_user(iid):
    feature = request.args['f']
    user = User.objects(iid=iid)[0]

    if feature == 'info':
        try:
            info = request.form
            username = info['username']
            existing_username = User.objects(username=username)
            if existing_username:

                # Save rest of data
                for key, value in info.items():
                    if key != 'username':
                        setattr(user, key, value)
                user.save()
                print('RETURNING')
                return {"message" : f"Another user is using that username"}, 400
            else:
                for key, value in info.items():
                    print(key)
                    setattr(user, key, value)
                user.save()
                return jsonify({'data' : 'Info updtate'})

        except Exception as e:
            print(e)
            return {'message' : 'Something went wrong'}, 500
    elif feature == 'avatar':
        img = request.files['file']
        if img:
            upload_result = cloudinary.uploader.upload(img)
            user.avatar = upload_result['url']
            user.save()
            return jsonify(upload_result)
    elif feature == 'playlist':
        song_id = request.form['song_id']
        if song_id in user.playlist:
            user.playlist.remove(song_id)

        else:
            user.playlist.append(song_id)

        user.save()
        print( list(user.playlist))
        return {'playlist' : user.playlist}

@router.route('/auth/confirm', methods=['POST'])
def confirm():

    token = request.args['token']

    if token:
        try:
            info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            user = User.objects(email=info['sub']).first()

            if user:
                user.is_verified = True
                user.save()

                user = user._data
                del user['password']
                user['id'] = str(user['id'])
                return {'user' : user, 'token' : token}

        except Exception as e:
            print(e)
            return {'message' : 'Something went wrong'}, 500
    return {'data': 'Conf'}


@router.route('/user/<iid>/terminate', methods=['POST'])
def terminate(iid):

    try:
        token = request.headers['Authorization'].split(' ')[1]

        if token:

            info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            if info:
                user = User.objects.get(email= info['user'])
                user.delete()
            return {'data' : 'User account deleted successfully'}
    except Exception as e:
        print(e)
        return {'message' : 'Something went wrong'}, 500

@router.route('/user/<iid>/confirm-password', methods=['POST'])
@jwt_required()
def confirm_pass(iid):

    try:
        email = get_jwt_identity()
        password = request.form['password']
        if email:
            user = User.objects(email=email).first()

            if user:
                pass_correct = bcrypt.check_password_hash(bytes(user.password, encoding='utf-8'), password)
                if pass_correct:
                    return 'Password correct', 200

                else:
                    return {"message" : "Incorrect password"}, 400

            else:

                return "Unauthorized", 401

    except Exception as e:
        print(e)
        return 'Something went wrong', 500