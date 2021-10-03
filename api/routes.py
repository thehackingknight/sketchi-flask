from flask import Flask,jsonify, request, Response, Blueprint
router = Blueprint('api', __name__)
from .models import Author, Track, Commen
import json
# from app import app


@router.route('/api/songs', methods=['GET'])
def api_songs():

    def clean_songs(song):

        song.uploader = song.uploader._data
        song  = song._data
        

        return song

    tracks = Track.objects()

    for song in tracks:
        uploader = song.uploader._data
        song.uploader = json.loads(song.uploader.to_json())
        del song.uploader['_id']
        #print(song.uploader)
        
        print(song.to_json())
    #songs  = list(map(clean_songs, tracks))
    #print(songs)
    return jsonify({'songs': 'songs'}), 200
    """
    def clean_songs(song):

        upldr = song.uploader
        upldr['id'] = str(upldr['id'])

        for s in upldr['songs']:
            print(s.title)
        del upldr['songs']
        song.uploader = upldr
        song = song._data
        song['id'] = str(song['id'])

        return song

    #print(list(map(clean_songs, tracks)))


    return {'songs' : list(map(clean_songs, tracks))}, 200"""
@router.route('/api', methods=['GET', 'POST'])
def api():

    if request.method == 'POST':

        try:

            author= Author()
            
            for key, val in request.form.items():
                setattr(author, key, val)
            iid = 'marind'
            author.iid = iid
            author.save()

            return request.form['username']

        except Exception as e:
            print(e)

        
    return 'API working'

@router.route('/api/song', methods=['GET', 'POST'])
def songs():

    if request.method == 'POST':
        try:

            action = request.args['action']
            uploader_id = request.args['uploaderId']
           
            
            if action == 'add':
                title = request.form['title']
                
                iid = 'swsjdf'

                song = Track()
                song.title = title
                song.iid = iid

                uploader = Author.objects(iid=uploader_id)[0]
                song.uploader = uploader
                
                song.save()
                uploader.songs.append(song)
                uploader.save()


                print(uploader)
            return 'Response'
        except Exception as e:
            print(e)
            return 'Exception'

@router.route('/api/<song_iid>/comment', methods=['POST', 'GET'])
def comments(song_iid):

    try:
        content = request.form['content']
        iid = 'marind'
        comment = Commen(content=content, by=Author.objects(iid=iid)[0])

        song = Track.objects(iid=song_iid)[0]
        song.comments.append(comment)
        song.save()
        return 'Comment added successfully'
    except Exception as e:
        print(e)
        return 'Something went wrong', 500