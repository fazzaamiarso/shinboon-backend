from pymongo.mongo_client import MongoClient
import os

# Create a new client and connect to the server
client = MongoClient(os.getenv("MONGO_URI"))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['newsletter']

subscribers_collection = db.get_collection("subscribers")
newsletter_collection = db.get_collection("newsletter")

if subscribers_collection == None:
    subscribers_collection = db.create_collection("subscribers")

if newsletter_collection == None:
    newsletter_collection = db.create_collection("newsletter")
