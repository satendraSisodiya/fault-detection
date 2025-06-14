import os 
import sys
import numpy as np
import pandas as pd 
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from typing import List, Tuple, Generator
from src.constant import *
from src.utils.main_utils import MainUtils
from src.exception import customException
from src.logger import logging
from dataclasses import dataclass

@dataclass 
class ModelTrainerConfig:
    artifact_folder = os.path.join(ARTIFACT_FOLDER)
    trained_model_path = os.path.join(artifact_folder, "model.pkl")
    expected_accuracy = 0.45
    model_config_file_path = os.path.join("config","model.yaml")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.utils = MainUtils()
        self.models = {
            "XGBClassifier" : XGBClassifier(),
            "GradientBoostingClassifier":GradientBoostingClassifier(),
            "RandomForestClassifier":RandomForestClassifier(),
            "SVC":SVC()
        }

    def evaluate_model(self, x, y, models):
        try:
            x_train, x_test, y_train, y_test = train_test_split(x,y,test_size = 0.2,random_state=42)
            report = {}   

            for i in range(len(list(models))):
                model = list(models.values())[i]
                model.fit(x_train, y_train)
                y_train_predict = model.predict(x_train) 
                y_test_predict = model.predict(x_test) 
                train_model_score = accuracy_score(y_train, y_train_predict)
                test_model_score = accuracy_score(y_test, y_test_predict)
                report[list(models.keys())[i]] = test_model_score

            return report

        except Exception as e:
            raise customException(e, sys) 


    def get_best_model(self,
                       x_train:np.array,
                       y_train:np.array,
                       x_test:np.array,
                       y_test:np.array
                       ):
        try:
            model_report:dict = self.evaluate_model(
                x_train = x_train,
                y_train = y_train,
                x_test = x_test,
                y_test = y_test,
                models = self.models
            )       

            best_model_score = max(sorted(model_report.values()))

            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]

            best_model_object = self.models[best_model_name]

            return best_model_name, best_model_score, best_model_object
        
        except Exception as e:
            raise customException(e, sys)
        

    def finetune_best_model(self, 
                       best_model_object:object,
                       best_model_name,
                       x_train,
                       y_train
                       ) -> object :
        try:
            model_param_grid = self.utils.read_yaml_file(self.model_trainer_config.model_config_file_path)["model_selection"]["model"][best_model_name]["search_param_grid"]

            grid_search = GridSearchCV(best_model_object, param_grid = model_param_grid, cv = 5, n_jobs = -1, verbose = 1)

            grid_search.fit(x_train, y_train)

            best_params = grid_search.best_params_

            print("best_params are: ", best_params)

            finetuned_model = best_model_object.set_params(**best_params)

            return finetuned_model
        
        except Exception as e:
            raise customException(e,sys)
        

    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info("Spliting training and testing input and target feature")

            x_train, y_train, x_test, y_test = (
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
            )
            
            logging.info("Extracting model config file path")

            model_report = self.evaluate_model(x = x_train, y = y_train, models = self.models)

            best_model_score = max(sorted(model_report.values()))

            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = self.models[best_model_name]
            best_model = self.finetune_best_model(best_model_object  = best_model,
                                                  best_model_name = best_model_name, 
                                                  x_train = x_train,
                                                  y_train = y_train
                                                  )
            best_model.fit(x_train,  y_train)
            y_predict = best_model.predict(x_test)
            best_model_score = accuracy_score(y_test, y_predict)

            print(f"best model name: {best_model_name} and score: {best_model_score}")

            if best_model_score < 0.5:
                raise Exception("No best model found with an accuracy greater than the threshold 0.5")
            
            logging.info("Best found model onn both training and testing datasets")
            logging.info(f"Saving model at path: {self.model_trainer_config.trained_model_path}")

            os.makedirs(os.path.dirname(self.model_trainer_config.trained_model_path), exist_ok = True)
            
            self.utils.save_object(file_path = self.model_trainer_config.trained_model_path, obj = best_model)

            return self.model_trainer_config.trained_model_path
        
        except Exception as e :
            raise customException(e,sys)