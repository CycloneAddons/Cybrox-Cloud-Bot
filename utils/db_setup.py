from pymongo import MongoClient

def setup_db():
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client['test']
    return db['files'], db['userclutches']
