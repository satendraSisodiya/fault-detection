import os
import sys
import pickle
import pandas as pd
from src.constant import *
from src.utils.main_utils import MainUtils
from flask import request
from dataclasses import dataclass
from src.exception import customException
from src.logger import logging

@dataclass
class PredictionPipelineConfig:
    artifact_folder = os.path.join(ARTIFACT_FOLDER)
    prediction_output_dirname:str = "predictions"
    prediction_file_name:str = "prediction_file.csv"
    model_file_path:str = os.path.join(artifact_folder, "model.pkl")
    preprocessor_path:str = os.path.join(artifact_folder, "preprocessor.pkl")
    prediction_file_path:str = os.path.join(prediction_output_dirname, prediction_file_name)

class PredictionPipeline:
    def __init__(self, request):
        self.request = request
        self.utils = MainUtils()
        self.prediction_pipeline_config = PredictionPipelineConfig()

    def save_input_file(self) -> str:
        try:
            pred_file_input_dir = "prediction_artifact"
            os.makedirs(pred_file_input_dir, exist_ok = True)
            input_csv_file = self.request.files["file"]
            pred_file_path = os.path.join(pred_file_input_dir, input_csv_file.filename)
            input_csv_file.save(pred_file_path)
            return pred_file_path
        
        except Exception as e:
            raise customException(e, sys)

    def predict(self, features):
        try:
            model = self.utils.load_object(self.prediction_pipeline_config.model_file_path)
            preprocessor = self.utils.load_object(file_path = self.prediction_pipeline_config.preprocessor_path)
            transformed_x = preprocessor.transform(features)
            preds = model.predict(transformed_x)
            return preds
        
        except Exception as e:
            raise customException(e, sys)
        
    def get_prediction_dataframe(self, input_data_dataframe_path:pd.DataFrame):
        try:
            prediction_column_name:str = TARGET_COLUMN

            input_df:pd.DataFrame = pd.read_csv(input_data_dataframe_path)
 
            input_df = input_df.drop(columns = "Unnamed: 0", errors="ignore") if "Unnamed: 0" in input_df.columns else input_df
 
            predictions = self.predict(input_df)
 
            input_df[prediction_column_name] = [pred for pred in predictions]
 
            target_column_mapping = {0:"bad", 1:"good"}
 
            input_df[prediction_column_name] = input_df[prediction_column_name].map(target_column_mapping)
 
            os.makedirs(self.prediction_pipeline_config.prediction_output_dirname, exist_ok = True)
 
            input_df.to_csv(self.prediction_pipeline_config.prediction_file_path, index = False)
 
            logging.info("Prediction completed")             

        except Exception as e:
            raise customException(e, sys)

    def run_pipeline(self):
        try:
            input_csv_path = self.save_input_file()
            self.get_prediction_dataframe(input_csv_path)
            return self.prediction_pipeline_config        
        except Exception as e:
            raise customException(e, sys)