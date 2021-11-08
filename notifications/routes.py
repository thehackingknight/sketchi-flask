from flask import request, Blueprint
from .models import Notifications
from user.models import User
from song.models import Song
import json, jwt, os
import time
from datetime import datetime
router = Blueprint('notification', __name__)

def validate(request):
    token = request.headers['Authorization'].split(' ')[1]
    info = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    return info


@router.route('/<user_id>/notifications', methods=['GET'])
def user_notifications(user_id):

    user = User.objects(iid=user_id).first()
    if user:
        notifications = Notifications.objects(to=user.iid, _from__ne=user.iid)

        def clean(notif):
            notif._from = json.loads(User.objects(iid=notif._from).first().to_json())
            return json.loads(notif.to_json())

        data = list(map(clean,notifications))
        return {'notifications' : data}
    else:
        return 'User not found', 404
    return 'Hang on'

@router.route('/notification/<oid>', methods=['GET', 'POST'])
def notif_by_id(oid):
    notif = Notifications.objects(pk=oid).first()
    params = request.args

    if notif:

        notif._from = json.loads(User.objects(iid=notif._from).first().to_json())
        data = json.loads(notif.to_json())
        return {'notif' : data}
    else:
        return 'No notification found for specified oid', 404

    return 'Hodo'

@router.route('/notification/<oid>/modify', methods=['POST'])
def modify(oid):
    notif = Notifications.objects(pk=oid).first()
    params = request.args

    if notif:
        if 'action' in params:
            act = params['action']
            if act == 'read':
                notif.is_read = True
                notif.save()
                return notif_by_id(oid)

            if act == 'delete':
                notif.delete()
                return 'Notification deleted'
    else:
        return 'No notification found for specified oid', 404
@router.route('/notifications/create',methods=['POST'])
def create():

    try:
        email = validate(request)['sub']
        user = User.objects(email=email).first()
        params = request.args
        action = params['action']
        target = params['target']
        if 'target_id' in params:
            target_id = params['target_id']

        notif = Notifications()
        if action == 'like':
            
            if target == 'song':

                song = Song.objects(iid=target_id).first()
                html = f"""liked your song <span class="a fw-5">{song.title}.</span>
                """
        if action == 'comment':
            target_element = params['target_element']
            song = Song.objects(iid=target_id).first()
            
            html = f"""commented on your song <span class="a fw-5">{song.title}.</span>
                """
            notif.target_element = target_element
        
        if action == 'reply':
            song = Song.objects(iid=target_id).first()
            
            target_element = params['target_element']
            
            notif.target_element = target_element
            uploader = User.objects(iid = song.uploader).first()
            html = f"""replied to your comment on <span class="a fw-5">{uploader.username}</span>'s song."""
        
        if action == 'follow':
            notif.target = params['target']
            html = f"""has started following you."""

        audience = json.loads(params['to'])
        notif.to = audience
        notif.target = params['target_id']
        notif._type = action
        notif.text = html
        notif._from = user.iid
        notif.secs_since_epoch= int(time.time())
        notif.date_created = datetime.now()
        notif.save()
        return notif_by_id(str(notif.id))
    except Exception as e:
        print(e)
        return 'Something went wrong', 500
