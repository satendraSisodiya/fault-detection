import os
import sys 
import pandas as pd
import numpy as np
from src.constant import *
from src.logger import logging
from src.utils.main_utils import MainUtils
from src.exception import customException
from dataclasses import dataclass
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, StandardScaler, FunctionTransformer

@dataclass
class DataTransformationConfig:
    artifact_folder = os.path.join(ARTIFACT_FOLDER)
    transformed_train_file_path = os.path.join(artifact_folder,"train.npy")
    transformed_test_file_path = os.path.join(artifact_folder,"test.npy")
    transformed_object_file_path = os.path.join(artifact_folder,"preprocessor.pkl")


class DataTransformation:
    def __init__(self, feature_store_file_path):
        self.feature_store_file_path = feature_store_file_path
        self.data_transformation_config = DataTransformationConfig()
        self.utils = MainUtils()

    def get_data(self, feature_store_file_path:str) -> pd.DataFrame:
        
        try:
            data = pd.read_csv(feature_store_file_path)
            print("[DEBUG] Columns before rename:", data.columns.tolist())
            data.rename(columns = {"Good/Bad" : TARGET_COLUMN}, inplace = True)
            print("[DEBUG] Columns after rename:", data.columns.tolist())  

            return data
        
        except Exception as e:
            raise customException(e, sys)

      
    def get_data_transformer_object(self):
        try:
            imputer_step = ("imputer", SimpleImputer(strategy="constant", fill_value=0))
            
            scaler_step= ("scaler", RobustScaler())

            preprocessor = Pipeline(
                steps = [
                    imputer_step,
                    scaler_step
                ]
            )

            return preprocessor
        
        except Exception as e:
            raise customException(e, sys)

    def intiate_data_transformation(self):
        logging.info("Entering intiate_data_transformation method of data_transformation class")

        try:
            df = self.get_data(feature_store_file_path = self.feature_store_file_path)

            x = df.drop(columns = TARGET_COLUMN) 
              
            y = np.where(df[TARGET_COLUMN] == -1,0,1)

            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

            preprocessor = self.get_data_transformer_object()

            x_train_scaled = preprocessor.fit_transform(x_train)

            x_test_scaled = preprocessor.transform(x_test)

            preprocessor_path = self.data_transformation_config.transformed_object_file_path

            os.makedirs(os.path.dirname(preprocessor_path),exist_ok = True)  
            
            self.utils.save_object(file_path = preprocessor_path, obj=preprocessor)

            train_arr = np.c_[x_train_scaled, np.array(y_train)]

            test_arr = np.c_[x_test_scaled, np.array(y_test)]
            
            return (train_arr, test_arr, preprocessor_path)


        except Exception as e:
            raise customException(e, sys)