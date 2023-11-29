import os
from configs import configs
import dataprocessing

import math

import matplotlib.pyplot as plt
import numpy as np
from tensorflow import keras
import joblib

def load_model(path):
    return keras.models.load_model(path)

def load_scaler(path):
    return joblib.load(path)

def prediction(model, scaler, sequence):
    predict_value = model.predict(sequence)
    predict_value_scaled = scaler.inverse_transform(predict_value)
    return predict_value_scaled

def evaluate_prediction(predictions, actual, model_name):
    errors = predictions - actual
    mse = np.square(errors).mean()
    rmse = np.sqrt(mse)
    mae = np.abs(errors).mean()
    print(model_name + ':')
    print('Mean Absolute Error: {:.4f}'.format(mae))
    print('Root Mean Square Error: {:.4f}'.format(rmse))
    print('')

def plot_future(prediction, actual_value, name):
    plt.plot(actual_value, c = 'b', label = "Actual Value")
    plt.plot(prediction, c = 'r', label = "Prediction")
    plt.xlabel("Timesteps")
    plt.ylabel("CPU Usage - %")
    plt.title(name)
    plt.legend()
    plt.show()

def predict_workload(model_path, scaler_path, data_path):
    loaded_model = load_model(model_path)
    loaded_scaler = load_scaler(scaler_path)
    if os.path.exists(data_path):
        df, check = dataprocessing.get_predict_data(data_path)
        if check >= configs.N_STEPS_IN:
            scaled_df = loaded_scaler.transform(df)
            sequense = dataprocessing.split_predict_sequences(scaled_df)
            future_request_value = prediction(loaded_model, loaded_scaler, sequense)
            future_request_value = list(future_request_value.flatten())
        else:
            future_request_value = [0,0]
    a = future_request_value[0]
    return a





