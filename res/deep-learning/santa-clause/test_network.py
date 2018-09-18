# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy
import argparse
import imutils
import cv2


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True, help="path to trained model")
ap.add_argument("-i", "--image", required=True, help="path to input image")
args = vars(ap.parse_args())

# load the image
image = cv2.imread(args["image"])
orig = image.copy()

# pre-process the image for classification
image_size = 28
image = cv2.resize(image, (image_size, image_size))
image = image.astype("float") / 255.0
image = img_to_array(image)
image = numpy.expand_dims(image, axis=0)  # after expanding, (1, width, height, 3) at channels last ordering

# load the trained convolutional neural network
print("[INFO] loading network...")
model = load_model(args["model"])

# classify the input image
(not_santa, santa) = model.predict(image)[0]

# build the label
label = "Santa" if santa > not_santa else "Not Santa"
proba = santa if santa > not_santa else not_santa
label = "{}: {:.2f}%".format(label, proba * 100)

# draw the label on the image
new_image_size = 400
output = imutils.resize(orig, width=new_image_size)
cv2.putText(output, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# show the output image
cv2.imshow("Output", output)
cv2.waitKey(0)

