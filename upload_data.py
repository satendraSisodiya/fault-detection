import pandas as pd
import json
from pymongo.mongo_client import MongoClient
from src.constant import *

# create client
client = MongoClient(MONGO_DB_URL)
db = client[MONGO_DATABASE_NAME]
collection = db[MONGO_COLLECTION_NAME]

# read csv file
df = pd.read_csv("C:\Users\saten\OneDrive\Desktop\sensorproject\notebook\wafer_23012020_041211.csv")

df = df.drop("Unnamed: 0", axis=1)

# json.load convert dataframe into key value pair in list
json_record = json.loads(df.to_json(orient="records"))

# the list of key value pair of sensors stored in mongoDB Atlas 
collection.insert_many(json_record)