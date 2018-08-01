# load data from mnist
from keras.datasets import mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

# check out the data
from keras.utils import to_categorical
import numpy as np
import matplotlib.pyplot as plt

print("Training data shape: ", train_images.shape, train_labels.shape)
print("Testing data shape: ", test_images.shape, test_labels.shape)

# find the unique numbers from the train labels
classes = np.unique(train_labels)
n_classes = len(classes)
print("Total number of outputs: ", n_classes)
print("Output classes: ", classes)

# plt.figure(figsize=[10,5])
# # display the first image in training data
# plt.subplot(121)
# plt.imshow(train_images[0,:,:], cmap="gray")
# plt.title("Ground Truth: {}".format(train_labels[0]))
# # display the first image in testing data
# plt.subplot(122)
# plt.imshow(test_images[0,:,:], cmap="gray")
# plt.title("Ground Truth: {}".format(test_labels[0]))
#
# plt.savefig("../res/digits/digits.jpg")


# PROCESS THE DATA
# change from matrix to array of dimension 28x28 to array of dimension 784
dim_data = np.prod(train_images.shape[1:])
train_data = train_images.reshape(train_images.shape[0], dim_data)
test_data = test_images.reshape(test_images.shape[0], dim_data)
# change to float datatype
train_data = train_data.astype("float32")
test_data = test_data.astype("float32")
# scale the data to lie between 0 to 1
train_data /= 255.0
test_data /= 255.0

# change the labels from integer to categorical data
train_labels_one_hot = to_categorical(train_labels)
test_labels_one_hot = to_categorical(test_labels)
# display the change for category label using one-hot encoding
print("Original label 0:", train_labels[0])
print("categorical (one-hot): ", train_labels_one_hot[0])


# TRAIN THE DATA
from keras.models import Sequential
from keras.layers import Dense, Dropout

model = Sequential()
model.add(Dense(512, activation="relu", input_shape=(dim_data,)))
model.add(Dropout(0.5))
model.add(Dense(512, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(n_classes, activation="softmax"))

model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])

history = model.fit(train_data, train_labels_one_hot, batch_size=256, epochs=20, verbose=1,
                    validation_data=(test_data, test_labels_one_hot))

[test_loss, test_acc] = model.evaluate(test_data, test_labels_one_hot)
print("Evaluation result on test data: loss = {}, accuracy = {}".format(test_loss, test_acc))


# # plot the loss curves
# plt.figure(figsize=[8,6])
# plt.plot(history.history["loss"],"r",linewidth=3.0)
# plt.plot(history.history["val_loss"],"b",linewidth=3.0)
# plt.legend(["Training loss", "Validation Loss"],fontsize=18)
# plt.xlabel("Epochs",fontsize=16)
# plt.ylabel("Loss",fontsize=16)
# plt.title("Loss Curves", fontsize=16)
# plt.savefig("../res/digits/loss_curves_with_dropout.jpg")
#
# #Plot the Accuracy Curves
# plt.figure(figsize=[8,6])
# plt.plot(history.history['acc'],'r',linewidth=3.0)
# plt.plot(history.history['val_acc'],'b',linewidth=3.0)
# plt.legend(['Training Accuracy', 'Validation Accuracy'],fontsize=18)
# plt.xlabel('Epochs',fontsize=16)
# plt.ylabel('Accuracy',fontsize=16)
# plt.title('Accuracy Curves',fontsize=16)
# plt.savefig("../res/digits/acc_curves_with_dropout.jpg")


# INFERENCE ON A SINGLE IMAGE
# predict the most likely class
model.predict_classes(test_data[[0],:])
# predict the probabilities for each class
model.predict(test_data[[0],:])
