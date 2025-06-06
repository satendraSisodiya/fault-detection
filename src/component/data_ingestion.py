import os
import sys
import numpy as np
import pandas as pd
from zipfile import Path
from src.logger import logging
from src.constant import *
from dataclasses import dataclass
from src.exception import customException
from src.utils.main_utils import MainUtils
from pymongo.mongo_client import MongoClient

@dataclass
class DataIngestionConfig:
    artifact_folder = os.path.join(ARTIFACT_FOLDER)


class DataIngestion:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.utils = MainUtils()

    def export_collection_as_dataframe(self,database_name, collection_name):
        try:
            # call the database collection
            mongo_client = MongoClient(MONGO_DB_URL)
            collection = mongo_client[database_name][collection_name]

            # Iterate the records 
            df = pd.DataFrame(list(collection.find()))
            
            # if the _id column present than drop that column
            if "_id" in df.columns.to_list():
                df = df.drop(columns = ["_id"], axis=1)
            
            # replace all null NaN() value to 
            df.replace({"na":np.nan}, inplace = True)

            return df        
        
        except Exception as e:
            raise customException(e, sys)
        
    def export_data_into_feature_store_file_path(self) -> pd.DataFrame:
        try:
            raw_file_path = self.data_ingestion_config.artifact_folder
            
            # if folder not exist  then create
            os.makedirs(raw_file_path, exist_ok = True)

            sensor_data = self.export_collection_as_dataframe(
                database_name = MONGO_DATABASE_NAME,
                collection_name = MONGO_COLLECTION_NAME
            )

            logging.info(f"saving exported data into feature_store_file_path:{raw_file_path}")
            feature_store_file_path = os.path.join(raw_file_path, "waffer-fault.csv")
            
            # dataframe (sensor_data) export to a csv file (feature_store_file_path)
            sensor_data.to_csv(feature_store_file_path, index = False)

            return feature_store_file_path

        except Exception as e:
            raise customException(e, sys)        
        

    def initiate_data_ingestion(self) -> Path :
        
        logging.info(f"Entered intiated_data_ingestion method of data_ingestion class")

        try:
            feature_store_file_path = self.export_data_into_feature_store_file_path()

            logging.info("got the data from mongoDB")
            logging.info("exited intiated_data_ingestion method of data_ingestion class") 
            return feature_store_file_path   
        
        except Exception as e:
            raise customException(e, sys)