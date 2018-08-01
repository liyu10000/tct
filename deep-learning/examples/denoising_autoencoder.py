import numpy as np
import sys
import tensorflow as tf
import matplotlib.pyplot as plt

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

inputs_ = tf.placeholder(tf.float32, [None,28,28,1])
targets_ = tf.placeholder(tf.float32, [None,28,28,1])


def lrelu(x, alpha=0.1):
    return tf.maximum(alpha*x, x)


### Encoder
with tf.name_scope('en-convolutions'):
    conv1 = tf.layers.conv2d(inputs_,filters=32,kernel_size=(3,3),strides=(1,1),padding='SAME',use_bias=True,activation=lrelu,name='conv1')
# Now 28x28x32
with tf.name_scope('en-pooling'):
    maxpool1 = tf.layers.max_pooling2d(conv1,pool_size=(2,2),strides=(2,2),name='pool1')
# Now 14x14x32
with tf.name_scope('en-convolutions'):
    conv2 = tf.layers.conv2d(maxpool1,filters=32,kernel_size=(3,3),strides=(1,1),padding='SAME',use_bias=True,activation=lrelu,name='conv2')
# Now 14x14x32
with tf.name_scope('encoding'):
    encoded = tf.layers.max_pooling2d(conv2,pool_size=(2,2),strides=(2,2),name='encoding')
# Now 7x7x32.
#latent space


# Decoder
with tf.name_scope('decoder'):
    conv3 = tf.layers.conv2d(encoded, filters=32, kernel_size=(3, 3), strides=(1, 1), name='conv3', padding='SAME',
                             use_bias=True, activation=lrelu)
    # Now 7x7x32
    upsample1 = tf.layers.conv2d_transpose(conv3, filters=32, kernel_size=3, padding='same', strides=2,
                                           name='upsample1')
    # Now 14x14x32
    upsample2 = tf.layers.conv2d_transpose(upsample1, filters=32, kernel_size=3, padding='same', strides=2,
                                           name='upsample2')
    # Now 28x28x32
    logits = tf.layers.conv2d(upsample2, filters=1, kernel_size=(3, 3), strides=(1, 1), name='logits', padding='SAME',
                              use_bias=True)
    # Now 28x28x1
    # Pass logits through sigmoid to get denoisy image
    decoded = tf.sigmoid(logits, name='recon')