'''
A Convolutional Network implementation example using TensorFlow library.
This example is using the MNIST database of handwritten digits
(http://yann.lecun.com/exdb/mnist/)

Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/
'''

from __future__ import print_function

import tensorflow as tf
import numpy as np

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
# mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)


x_set = np.array([]).reshape(0, 50, 50, 1)
y_set = np.array([]).reshape(0, 2)
for it in range(6):
    x_tmp = np.load("data/xtrain_50_" + str(it) + ".dat")
    y_tmp = np.load("data/ytrain_50_" + str(it) + ".dat")
    print(x_tmp.shape)
    print(y_tmp.shape)
    x_set = np.append(x_set, x_tmp, axis=0)
    y_set = np.append(y_set, y_tmp, axis=0)
print(x_set.shape)
print(y_set.shape)
exit()
x_set2 = np.load("xtrain_50_2.dat")
y_set2 = np.load("ytrain_50_2.dat")
x_set = np.squeeze(x_set)
x_set2 = np.squeeze(x_set2)

x_test = x_set[3000:4000]
y_test = y_set[3000:4000]

x_set = x_set[:3000]
y_set = y_set[:3000]
print(x_set.shape)
x_set = np.concatenate((x_set, x_set2))
y_set = np.concatenate((y_set, y_set2))
taille_set = x_set.shape[0]




# Parameters
learning_rate = 0.00001
training_iters = 200
batch_size = 25
display_step = 10

# Network Parameters
n_input = 50*50 # MNIST data input (img shape: 28*28)
img_size = 50
n_classes = 2 # MNIST total classes (0-9 digits)
dropout = 0.5 # Dropout, probability to keep units

# tf Graph input
x = tf.placeholder(tf.float32, [None, img_size, img_size])
y = tf.placeholder(tf.float32, [None, n_classes])
keep_prob = tf.placeholder(tf.float32) #dropout (keep probability)


# Create some wrappers for simplicity
def conv2d(x, W, b, strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                          padding='SAME')


# Create model
def conv_net(x, weights, biases, dropout):
    # Reshape input picture
    x = tf.reshape(x, shape=[-1, img_size, img_size, 1])

    # Convolution Layer
    conv1 = conv2d(x, weights['wc1'], biases['bc1'])
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1, k=2)

    # print(conv1.shape) # pr avoir size pr wd1 X*X*32

    # Convolution Layer
    conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2, k=2)

    print(conv2.shape)
    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    # Apply Dropout
    fc1 = tf.nn.dropout(fc1, dropout)

    # Output, class prediction
    out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
    return out

# Store layers weight & bias
weights = {
    # 5x5 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
    # 5x5 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([13*13*64, 1024])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, n_classes]))
}

biases = {
    'bc1': tf.Variable(tf.random_normal([32])),
    'bc2': tf.Variable(tf.random_normal([64])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# Construct model
pred = conv_net(x, weights, biases, keep_prob)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))


# prediction
prediction = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))

# Initializing the variables
init = tf.global_variables_initializer()

# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    best_accuracy = 0
    # batch_x, batch_y = mnist.train.next_batch(batch_size)
    for i in range(int(taille_set/batch_size)):
        batch_x = x_set[i*batch_size:(i+1)*batch_size]
        batch_y = y_set[i*batch_size:(i+1)*batch_size]
        if batch_x.shape[0] == 0:
            break
        # Run optimization op (backprop)
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y,
                                           keep_prob: dropout})
        # Calculate batch loss and accuracy
        loss, acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                          y: batch_y,
                                                          keep_prob: 1.})
        print("Minibatch Loss= " + "{:.6f}".format(loss) + ", Training Accuracy= " + "{:.5f}".format(acc))
        if acc > best_accuracy:
            best_accuracy = acc
    
    print("Optimization Finished!")
    print("Best training accuracy : %f" % best_accuracy)
    res = sess.run(prediction, feed_dict={x: x_test, y: y_test, keep_prob: 1})
    loss, acc = sess.run([cost, accuracy], feed_dict={x: x_test,
                                                      y: y_test,
                                                      keep_prob: 1.})
    print(res)
    print("Accuracy : %f\n" % acc)