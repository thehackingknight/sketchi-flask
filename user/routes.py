
from flask import Flask,jsonify, request, Response, Blueprint

from user.models import User
from song.models import Song
from temps.models import TempPath
import song.routes as song_routes
import jwt, datetime,json,random, string, uuid
from dotenv import load_dotenv
import os, cloudinary,json, requests, re
import cloudinary.uploader
from flask_bcrypt import Bcrypt
from random import *
from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from media.models import Media

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
    songs = Song.objects(uploader=uploader_id)
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
                    font: medium/ 1.5  Arial,Helvetica,sans-serif !important;
                    margin: auto;
                    padding: 10px;
                    color: black;
                   
                }}
    
    
                   
                  
    
                .btn {{
                    cursor: pointer;
                    display: inline-block;
                    min-height: 1em;
                    outline: 0;
                    border: none;
                    vertical-align: baseline;
                    background: #e0e1e2 none;
                    color: rgba(0,0,0,.6);
                    font-family: Lato,"Helvetica Neue",Arial,Helvetica,sans-serif;
                    margin: 0 .25em 0 0;
                    padding: .78571429em 1.5em;
                    text-transform: none;
                    text-shadow: none;
                    font-weight: 600;
                    line-height: 1em;
                    font-style: normal;
                    text-align: center;
                    text-decoration: none;
                    border-radius: .28571429rem;
                    box-shadow: inset 0 0 0 1px transparent,inset 0 0 0 0 rgba(34,36,38,.15);
                    -webkit-user-select: none;
                    -ms-user-select: none;
                    user-select: none;
                    transition: opacity .1s ease,background-color .1s ease,color .1s ease,box-shadow .1s ease,background .1s ease;
                    will-change: "";
                    -webkit-tap-highlight-color: transparent;
                }}
                .btn-primary {{
                    color: #fff !important;
                    background-color: #0d6efd !important;
                    border-color: #0d6efd !important;
                    
                }}
        </style>
    </head>
    <body>
    
        <div class="sketchi">
    
        <h1>Thank you for signing up to Sketchi!</h1>
    
        <p>To finish up, Click the button to verify your account.</p>
        <a href="{url}" target="_blank" class="btn btn-primary">Verify</a>
        
        <p>If button did not work use this link:</p>
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
            email = validate(request)['sub']
            print(email)
            user = User.objects(email = email)
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
                email = validate(request)['sub']
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
                email = email = validate(request)['sub']

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

def validate(request):
    token = request.headers['Authorization'].split(' ')[1]
    info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    return info

@router.route('/user/<iid>/update', methods=['GET', 'POST'])
@jwt_required()
def update_user(iid):

    params = request.args
    feature = params['f']

    
    email = validate(request)['sub']
    info = request.form
    if email:
        user = User.objects(email=email).first()
        if feature == 'followers':
            artist = User.objects(iid=iid).first()
            if params['action'] == 'follow':
                artist.followers.append(user.iid)
                artist.save()

                user.following.append(artist.iid)
                user.save()
                
                return {'followers' : artist.followers}
            else:
                artist.followers.remove(user.iid)
                user.following.remove(artist.iid)

                artist.save()
                user.save()
                return {'followers' : artist.followers}
        if feature == 'info':
            try:
                
                username = info['username']
                existing_username = User.objects(username=username)
                if existing_username:

                    # Save rest of data
                    for key, value in info.items():
                        if key != 'username':
                            setattr(user, key, value)
                    user.save()
                    if user.username == username:
                        return 'Done', 200
                    else:                
                        return {"message" : f"Another user is using that username"}, 400
                else:
                    for key, value in info.items():
                        setattr(user, key, value)
                    user.save()
                    return jsonify({'data' : 'Info updtate'})

            except Exception as e:
                print(e)
                return {'message' : 'Something went wrong'}, 500
        if feature == 'avatar':
            img = request.files['file']
            if img:
                #upload_result = cloudinary.uploader.upload(img)
                #user.avatar = upload_result['url']
                image = Media()
                image.name = 'sketchi_' + uuid.uuid4().hex
                image._type = "image"
                image._file.put(img, content_type=img.mimetype)
                image.save()

                print('Checking old image...')
                old_image = None
                try:
                    old_image = Media.objects(id=str(user.avatar.split('/')[-1])).first()
                except Exception as e:
                    pass
                    if old_image:
                        old_image.delete()
                        print('Old image deleted')
                user.avatar = os.getenv('DB_URL') + '/media/images/' + str(image.id)
                user.save()
                return jsonify({'url' : user.avatar})
        if feature == 'playlist':
            song_id = request.form['song_id']
            if song_id in user.playlist:
                user.playlist.remove(song_id)

            else:
                user.playlist.append(song_id)

            user.save()
            print( list(user.playlist))
            return {'playlist' : user.playlist}
    else:
        print('Invalid Token')
        return {'message' : 'Invalid token'}, 401

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

            if str(e) == 'Signature verification failed':
                return {'message' : 'Invalid Token'}, 401
            return {'message' : 'Something went wrong'}, 500
    return {'data': 'Conf'}


@router.route('/auth/forgot', methods=['POST'])
def forgot():

    try:
        email = request.form['email']
        user = User.objects(email=email).first()
        if user:
            tp = TempPath()
            tp.user = email
            tp.save()

            message = f"""<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style type="text/css">


            .sketchi{{
                     font: medium/ 1.5  Arial,Helvetica,sans-serif !important;
                margin: auto;
                padding: 10px;
        }}

            .sketchi *, .sketchi{{
                -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none;
            }}

            .sketchi::-webkit-scrollbar{{
                display: none;
              }}

            .btn {{
                display: inline-block;
                font-weight: 400;
                line-height: 1.5;
                color: #212529;
                text-align: center;
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
                transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;}}
            .btn-primary {{
                color: #fff;
                background-color: #0d6efd;
                border-color: #0d6efd;
            }}

            .brand{{
                font-weight: 800
            }}
            .red{{
                background-color: #db2828;
                color: #fff !important;
                text-shadow: none;
                background-image: none;
            }}
    </style>
</head>
<body>

    <div class="sketchi">

        <h1 style="font-size: 24px">Reset Password</h1>
        <p>You have requested to reset your password for your <a href="{os.getenv('CLIENT_URL')}" class="brand">Snaredrum</a> account.</p>

        <a style="font-weight: normal" class="red btn"  href="{os.getenv('CLIENT_URL') + '/auth/reset/' + str(tp.id)}">Reset password</a>

        <p>

            If button does not work, use this url: 
            <a href="{os.getenv('CLIENT_URL') + '/auth/reset/' + str(tp.id)}">{os.getenv('CLIENT_URL') + '/auth/reset/' + str(tp.id)}</a>
        </p>
    <p>For support please contact us at <a href="mailto:clickbait4587@gmail.com">clickbait4587@gmail.com</a></p>
    </div>
    
</body>
</html>"""

            try:
                send_email('Recover password', message, [email], res=None)
            except Exception as e:
                print(e)
                return {"message" : 'Something went wrong. We could not send the email.'}, 500
        else:
            return {'message' : 'No user with specified email found!'},404
        return 'Hang on'

    except Exception as e:
        print(e)
        return {"message" : 'Something went wrong'}, 500

@router.route('/auth/reset',methods=['POST'])
def reset():

    if request.method  == 'POST':
        try:
            oid = request.args['oid']
            temp = TempPath.objects(pk=oid).first()
            if temp:
                user = User.objects(email = temp.user).first()

                password = request.form['password']
                hashed_pass = bcrypt.generate_password_hash(password)
                user.password = hashed_pass.decode()
                temp.delete()
                return "Password reset successful!"

            else:
                return {'message' : 'UNAUTHORIZED'}, 401
        except Exception as e:
            print(e)
            return {"message" : 'Something went wrong'}, 500
@router.route('/user/<iid>/terminate', methods=['POST'])
def terminate(iid):

    try:
        token = request.headers['Authorization'].split(' ')[1]

        if token:

            info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            if info:
                user = User.objects.get(email= info['sub'])

                image = None
                try:
                    image = Media.objects(pk=user.avatar.split('/')[-1]).first()
                except Exception as e:
                    pass
                if image:
                    image.delete()
                    print('Avatar deleted')
                
                for song_id in user.songs:

                    song = Song.objects(iid = song_id).first()
                    if song:
                        song_image = None
                        song_file = None
                        try:
                            song_image = Media.objects(pk = song.image.split('/')[-1]).first()
                            song_file = Media.objects(pk = song.url.split('/')[-1]).first()
                        except Exception as e:
                            pass
                        if song_image:
                            song_image.delete()
                            print(song.title + ' Cover deleted')
                        if song_file:
                            song_file.delete()
                            print(song.title + ' File deleted')

                        song.delete()
                        print('Song deleted')
                user.delete()
            return {'data' : 'User account deleted successfully'}
    except Exception as e:
        print(e)
        return {'message' : 'Something went wrong'}, 500

@router.route('/user/<iid>/confirm-password', methods=['POST'])
@jwt_required()
def confirm_pass(iid):

    try:
        email = email = validate(request)['sub']
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

@router.route('/delpic/<oid>', methods=['POST'])
def delpic(oid):
    print(oid)
    try:
        img = Media.objects(pk=oid)
    except Exception as e:
        print(e)
    return 'working'