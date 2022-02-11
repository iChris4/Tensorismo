#!/usr/bin/env python

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras import optimizers
from tensorflow.keras import backend as K
import tensorflow as tf
import sklearn
import matplotlib.pyplot as plt
from utils import Sample

# Global variable
OUT_SHAPE = 5
INPUT_SHAPE = (Sample.IMG_H, Sample.IMG_W, Sample.IMG_D)


def customized_loss(y_true, y_pred, loss='euclidean'):
    # Simply a mean squared error that penalizes large joystick summed values
    if loss == 'L2':
        L2_norm_cost = 0.001
        val = K.mean(K.square((y_pred - y_true)), axis=-1) \
                    + K.sum(K.square(y_pred), axis=-1)/2 * L2_norm_cost
    # euclidean distance loss
    elif loss == 'euclidean':
        val = K.sqrt(K.sum(K.square(y_pred-y_true), axis=-1))
    return val


def create_model(keep_prob = 0.8):
    model = Sequential()

    # NVIDIA's model
    model.add(Conv2D(24, kernel_size=(5, 5), strides=(2, 2), activation='elu', input_shape= INPUT_SHAPE))
    model.add(Conv2D(36, kernel_size=(5, 5), strides=(2, 2), activation='elu'))
    model.add(Conv2D(48, kernel_size=(5, 5), strides=(2, 2), activation='elu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='elu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='elu'))
    model.add(Flatten())
    #model.add(Dense(1164, activation='elu'))
    drop_out = 1 - keep_prob
    model.add(Dropout(drop_out))
    model.add(Dense(100, activation='elu'))
    model.add(Dropout(drop_out))
    model.add(Dense(50, activation='elu'))
    model.add(Dropout(drop_out))
    model.add(Dense(10, activation='elu'))
    model.add(Dropout(drop_out))
    model.add(Dense(OUT_SHAPE))

    return model


if __name__ == '__main__':
    # Load Training Data
    x_train = np.load("data/X.npy")
    y_train = np.load("data/y.npy")
    #x_train, y_train = sklearn.utils.shuffle(x_train, y_train)
    print(x_train.shape[0], 'train samples')

    # Training loop variables
    epochs = 150
    batch_size = 90
    learning_rate=0.00001

    model = create_model()
    model.compile(loss='mse', optimizer=optimizers.Adam(learning_rate=learning_rate))
    callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=100)
    history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, shuffle=True, validation_split=0.1, callbacks=[callback])

    # summarize history for accuracy
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()

    print ("Epochs : " + str(epochs))
    print ("Batch : " + str(batch_size))
    print ("Learning rate : " + str(learning_rate))

    model.save_weights('model_weights.h5')
