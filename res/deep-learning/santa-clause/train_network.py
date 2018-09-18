# set the matplotlib backend so figures can be saved in the background
import matplotlib
matplotlib.use("AGG")

# import the necessary packages
from keras.preprocessing.image import ImageDataGenerator, img_to_array
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from imutils import paths
from matplotlib import pyplot
import numpy
import argparse
import random
import cv2
import os

# # not required
# from pyimagesearch.lenet import LeNet
from lenet import LeNet

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True, help="path to input dataset")
ap.add_argument("-m", "--model", required=True, help="path to output model")
ap.add_argument("-p", "--plot", type=str, default="plot.png", help="path to output accuracy/loss plot")
args = vars(ap.parse_args())

# initialize the number of epochs to train for, initial learning rate, and batch size
epochs = 25
learning_rate = 1e-3
batch_size = 32
image_size = 28

# initialize the data and labels
print("[INFO] loading images...")
data = []
labels = []

# grab the image paths and randomly shuffle them
imagePaths = sorted(list(paths.list_images(args["dataset"])))
random_seed = 42
random.seed(random_seed)
random.shuffle(imagePaths)

# loop over the input images
for imagePath in imagePaths:
    # load the image, pre-process it, and store it in the data list
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (image_size, image_size))
    image = img_to_array(image)
    data.append(image)

    # extract the class label from the image path and update the labels list
    label = imagePath.split(os.path.sep)[-2]
    label = 1 if label == "santa" else 0
    labels.append(label)

# scale the row pixel intensities to the range [0,1]
data = numpy.array(data, dtype="float") / 255.0
labels = numpy.array(labels)

# partition the data into training and testing splits using 75% of the data
# for training and the remaining 25% for testing
partition_percentage = 0.25
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=partition_percentage, random_state=random_seed)

# convert the labels from integers to vectors
trainY = to_categorical(trainY, num_classes=2)
testY = to_categorical(testY, num_classes=2)

# construct the image generator for data augmentation
aug = ImageDataGenerator(rotation_range=30,
                         width_shift_range=0.1,
                         height_shift_range=0.1,
                         shear_range=0.2,
                         zoom_range=0.2,
                         horizontal_flip=True,
                         fill_mode="nearest")

# initialize the model
print("[INFO] compiling model...")
model = LeNet.build(width=image_size, height=image_size, depth=3, classes=2)
opt = Adam(lr=learning_rate, decay=learning_rate/epochs)
model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

# train the network
print("[INFO] training network...")
H = model.fit_generator(aug.flow(trainX, trainY, batch_size=batch_size),
                        validation_data=(testX, testY), steps_per_epoch=len(trainX)//batch_size,
                        epochs=epochs, verbose=1)

# save the model to disk
print("[INFO] serializing network...")
model.save(args["model"])

# plot the training loss and accuracy
print("[INFO] ploting learning curve...")
pyplot.style.use("ggplot")
pyplot.figure()
N = epochs
pyplot.plot(numpy.arange(0, N), H.history["loss"], label="train_loss")
pyplot.plot(numpy.arange(0, N), H.history["val_loss"], label="val_loss")
pyplot.plot(numpy.arange(0, N), H.history["acc"], label="train_acc")
pyplot.plot(numpy.arange(0, N), H.history["val_acc"], label="val_acc")
pyplot.title("Training Loss and Accuracy on Santa/Non-Santa")
pyplot.xlabel("Epoch #")
pyplot.ylabel("Loss/Accuracy")
pyplot.legend(loc="lower left")
pyplot.savefig(args["plot"])