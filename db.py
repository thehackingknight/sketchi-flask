import pymongo
import mongoengine as engine

try:
    engine.connect(db='sketchi', host='localhost', port=27017)
    print('Database connection established')
except Exception as e:
    print(e)

"""
try:
    mongo = pymongo.MongoClient(
        host="localhost",
        port=27017,
        serverSelectionTimeoutMS = 1000
    )

    # Choose Database name
    db = mongo.sketchi
    print()
    mongo.server_info()  # Trigger exception if connection fails
    print('Database connected')
except Exception as e:
    print('Cannot cannot connect to db')
    print(e)"""