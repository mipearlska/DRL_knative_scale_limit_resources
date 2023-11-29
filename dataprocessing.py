import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from numpy import array
import joblib
from configs import configs

def get_predict_data(path):
    dataset = pd.read_csv(path, header=None)
    dataset = dataset[0].values
    check = len(dataset)
    dataset = dataset.reshape(len(dataset), 1)
    return dataset, check
def split_predict_sequences(sequences):
    x = configs.N_STEPS_IN
    seq_data = sequences[-x:]
    seq_data = array(seq_data)
    seq_data = seq_data.reshape(1, configs.N_STEPS_IN, configs.N_STEPS_OUT)
    return seq_data
def split_sequences(sequences, n_steps_in, n_steps_out):
    data, labels = [], []
    for i in range(len(sequences)):
        end_ix = i + n_steps_in
        out_end_ix = end_ix + n_steps_out
        if out_end_ix > len(sequences):
            break
        seq_data = sequences[i:end_ix]
        seq_labels = sequences[end_ix:out_end_ix, 0]
        data.append(seq_data)
        labels.append(seq_labels)
    return array(data), array(labels)

def save_scaler(dataset):
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset_scaled = scaler.fit_transform(dataset)
    joblib.dump(scaler, './scaler/scaler.pkl')
    return dataset_scaled

def get_train_data(path):
    dataset = pd.read_csv(path)
    dataset = dataset[0].values
    dataset = dataset.reshape(len(dataset), 1)
    dataset_scaled = save_scaler(dataset)
    return dataset_scaled

def split_data(df):
    split_point = int(len(df)*0.8)
    train_dataset = df[:split_point, :]
    test_dataset = df[split_point:, :]
    return train_dataset, test_dataset


