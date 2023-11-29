#from tensorflow.keras.models import Sequential
from keras.models import Sequential
#from tensorflow.keras.layers import Dense,LSTM,Activation, Dropout, Bidirectional
from keras.layers import Dense,LSTM,Activation, Dropout, Bidirectional
#from tensorflow.keras.callbacks import EarlyStopping
from keras.callbacks import EarlyStopping

def create_model_bilstm(num_units, train_x):
    model = Sequential()
    model.add(Bidirectional(LSTM(units=num_units, return_sequences=True),
              input_shape=(train_x.shape[1], train_x.shape[2])))
    model.add(Bidirectional(LSTM(units=num_units)))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')
    return model

def fit_model(model, num_epochs, num_batch_size, train_x, train_y):
    early_stop = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)
    history = model.fit(train_x, train_y, validation_split=0.2, epochs = num_epochs, batch_size=num_batch_size, callbacks=[early_stop])
    return history

def save_model(model, name):
    model.save('./model/{}'.format(name))



