import os,sys
from src.logger import logging 
from src.exception import customException
from src.pipeline.training_pipeline import TrainingPipeline
from src.pipeline.prediction_pipeline import PredictionPipeline
from flask import Flask, render_template, jsonify, request, send_file


app = Flask(__name__)

training_completed = False

@app.route("/")
def home():
    global training_completed
    return render_template("home.html", training_done=training_completed)


@app.route("/train")
def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        training_completed = True  # Update flag after successful training
        return render_template("home.html", training_done=True)

    except Exception as e:
        raise customException(e,sys)


@app.route('/predict', methods=['POST', 'GET'])
def upload():
    try:
        if request.method == 'POST':
            # it is a object of prediction pipeline
            prediction_pipeline = PredictionPipeline(request)
           
            #now we are running this run pipeline method
            prediction_file_detail = prediction_pipeline.run_pipeline()


            logging.info("prediction completed. Downloading prediction file.")
            return send_file(prediction_file_detail.prediction_file_path,
                            download_name= prediction_file_detail.prediction_file_name,
                            as_attachment= True)
        
        else:
            return render_template('upload_file.html')
    except Exception as e:
        raise customException(e,sys)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug= True)