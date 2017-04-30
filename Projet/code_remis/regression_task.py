from __future__ import print_function
import cv2
import numpy as np
import scipy.io as sio
import keras
import h5py
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import regularizers
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.stats import norm

batch_size = 128
num_classes = 2
epochs = 30
data_augmentation = True

# The data, shuffled and split between train and test sets:

'''f = h5py.File('DataSetXX.mat')
x = f["datasetx"]
x_data=np.array(x)'''
x_data=sio.loadmat('data')['DataSetX']
y_data=sio.loadmat('age')['DataSetAge']


x_data=np.reshape(x_data,(x_data.shape[0],3,64,64))

x_train=x_data[:int(np.shape(x_data)[0]*0.7),:,:,:]
x_valid=x_data[int(np.shape(x_data)[0]*0.7):int(np.shape(x_data)[0]*0.85),:,:,:]
x_test=x_data[int(np.shape(x_data)[0]*0.85):,:,:]

y_train=y_data[:int(np.shape(y_data)[0]*0.7)]
y_valid=y_data[int(np.shape(y_data)[0]*0.7):int(np.shape(y_data)[0]*0.85)]
y_test=y_data[int(np.shape(y_data)[0]*0.85):]
 
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
'''y_train = keras.utils.to_categorical(y_train, num_classes)
y_valid= keras.utils.to_categorical(y_valid, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)'''

model = Sequential()

model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:], kernel_initializer='he_normal', activation='relu'))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3), kernel_initializer='he_normal'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same',kernel_initializer='he_normal'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3),kernel_initializer='he_normal'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512,kernel_initializer='he_normal'))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(256,kernel_initializer='he_normal'))
model.add(Dropout(0.5))
model.add(Dense(1))

# Let's train the model using RMSprop
model.compile(loss='mean_absolute_error',
              optimizer='rmsprop',
              metrics=['mae'])

x_train = x_train.astype('float32')
x_valid= x_valid.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_valid /=255
x_test /= 255

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_valid, y_valid),
              shuffle=True)
    model_evaluate=model.evaluate(x_test,y_test,verbose=1)
    print('\n',model_evaluate[1])
    predict=model.predict(x_test,verbose=1)+2
    f=open('predict.txt','w')
    for i in range(len(predict)):
        s=str(predict[i])+','+str(y_test[i])+'\n'
        f.write(s)
        
    diff=(predict-y_test)
    print(diff)
    n, bins, patches = plt.hist(diff, 80)
    (mu, sigma) = norm.fit(diff)
    distribution = mlab.normpdf( bins, mu, sigma)
    show = plt.plot(bins, distribution*y_test.shape[0], 'r--', linewidth=2)

else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=5,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for feature-wise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(x_train)

    # Fit the model on the batches generated by datagen.flow().
    model.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        steps_per_epoch=x_train.shape[0] // batch_size,
                        epochs=epochs,
validation_data=(x_test, y_test))
    
    model_evaluate=model.evaluate(x_test,y_test,verbose=1)
    print('\n',model_evaluate[1])
    predict=model.predict(x_test,verbose=1)+2
    f=open('predict.txt','w')
    for i in range(len(predict)):
        s=str(predict[i])+','+str(y_test[i])+'\n'
        f.write(s)
        
    diff=(predict-y_test)
    print(diff)
    n, bins, patches = plt.hist(diff, 80)
    (mu, sigma) = norm.fit(diff)
    distribution = mlab.normpdf( bins, mu, sigma)
    show = plt.plot(bins, distribution*y_test.shape[0], 'r--', linewidth=2)
    plt.xlabel('Erreur')
    plt.ylabel('Nombre occurences')
    plt.title(r'$\mathrm{Histogram\ of\ errors:}\ \mu=%.3f,\ \sigma=%.3f$' %(mu, sigma))
    plt.grid(True)
    plt.show()