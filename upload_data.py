import pandas as pd
import json
from pymongo.mongo_client import MongoClient
from src.constant import *

# create client
client = MONGO_DB_URL

# read csv file
df = pd.read_csv("C:\Users\saten\OneDrive\Desktop\sensorproject\notebook\wafer_23012020_041211.csv")

df = df.drop("Unnamed:0", axis=1)

# json.load convert dataframe into key value pair in list
json_record = list(json.load(df.T.to_json()).values())

# the list of key value pair of sensors stored in mongoDB Atlas 
client[MONGO_DATABASE_NAME][MONGO_COLLECTION_NAME].insert_many(json_record)