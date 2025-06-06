import sys
from src.component.data_ingestion import DataIngestion
from src.component.data_transformation import DataTransformation
from src.component.model_trainer import ModelTrainer
from src.exception import customException

class TrainingPipeline:
    def start_data_ingestion(self):
        try:
            data_ingestion = DataIngestion()
            feature_store_file_path = data_ingestion.initiate_data_ingestion()
            return feature_store_file_path
        
        except Exception as e:
            raise customException(e, sys)

    def start_data_transformation(self, feature_store_file_path):
        try:
            data_transformation = DataTransformation(feature_store_file_path = feature_store_file_path)
            train_arr, test_arr, preprocessor  =  data_transformation.intiate_data_transformation()
            return train_arr, test_arr, preprocessor

        except Exception as e:
            raise customException(e, sys)

    def start_model_trainer(self, train_arr, test_arr):
        try:
            model_trainer = ModelTrainer()
            model_score = model_trainer.initiate_model_trainer(train_arr, test_arr)
            return model_score
        
        except Exception as e:
            raise customException(e, sys)        
        
    def run_pipeline(self):
        try:
            feature_store_file_path = self.start_data_ingestion()
            train_arr, test_arr, preprocessor_path = self.start_data_transformation(feature_store_file_path = feature_store_file_path)
            r2_square = self.start_model_trainer(train_arr = train_arr, test_arr = test_arr)
            print(f"Training completed. Trained model score: {r2_square}")

        except Exception as e:
            raise customException(e, sys)    