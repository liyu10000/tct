## Image Categorization
This CNN model serves to classify and clarify which category the input image belongs to, before cell detection. It will contribute to the confirmation of detected cells, and save time to some extent.

### Training
1. train1
 - _cnnmodel_: keras/xception
 - _dataset_: The data comes from resizing of darknet/train13. Resized image dimension is 299x299.
 - _weights_: pretrained on imagenet

2. train2
 - _cnnmodel_: caffe/resnet50
 - _dataset_: The data comes from resizing of darknet/train13. It was first resized to 299x299 as xception input but was soon found to be too slow at training. After further resizing to 224x224, it was made into lmdb database for caffe.
 - _weights_: resnet50_cvgj_iter_320000.caffemodel
 - _crop_size_: set to 224
 
3. train3
 - _cnnmodel_: caffe/resnet50
 - _dataset_: The same lmdb as with train2
 - _weights_: resnet50_cvgj_iter_320000.caffemodel
 - _crop_size_: removed

4. train4
 - _cnnmodel_: caffe/resnet50
 - _dataset_: Same lmdb database from train2, set aside SC from NORMAL, added some more NORMAL data.
 - _weights_: resnet50_cvgj_iter_320000.caffemodel
 - _crop_size_: removed

5. train5
 - _cnnmodel_: keras/xception
 - _dataset_: The data comes from resizing of darknet/train13. Resized image dimension is 299x299.
 - _weights_: pretrained on imagenet
 
<pre>
Found 10469560 images belonging to 13 classes.
Found 1154324 images belonging to 13 classes.
Epoch 1/1
81794/81794 [==============================] - 218679s 3s/step - loss: 1.2684 - acc: 0.5800 - val_loss: 1.9611 - val_acc: 0.4108

Found 10469560 images belonging to 13 classes.
Found 1154324 images belonging to 13 classes.
Epoch 3/100
163587/163587 [==============================] - 141539s 865ms/step - loss: 0.0638 - acc: 0.9792 - val_loss: 0.1571 - val_acc: 0.9564

Epoch 00003: saving model to batch6.3_003_0.1571.hdf5
Epoch 4/100
163587/163587 [==============================] - 165272s 1s/step - loss: 0.0504 - acc: 0.9837 - val_loss: 0.1180 - val_acc: 0.9657

Epoch 00004: saving model to batch6.3_004_0.1180.hdf5
Epoch 5/100
163587/163587 [==============================] - 192295s 1s/step - loss: 0.0441 - acc: 0.9859 - val_loss: 0.4775 - val_acc: 0.9371

Epoch 00005: saving model to batch6.3_005_0.4775.hdf5
Epoch 6/100
163587/163587 [==============================] - 192979s 1s/step - loss: 0.0301 - acc: 0.9903 - val_loss: 0.1810 - val_acc: 0.9585

Epoch 00006: saving model to batch6.3_006_0.1810.hdf5
Epoch 7/100
163587/163587 [==============================] - 193230s 1s/step - loss: 0.0232 - acc: 0.9926 - val_loss: 0.2915 - val_acc: 0.9485

Epoch 00007: saving model to batch6.3_007_0.2915.hdf5
Epoch 8/100
163587/163587 [==============================] - 193029s 1s/step - loss: 0.0203 - acc: 0.9935 - val_loss: 0.1412 - val_acc: 0.9675

Epoch 00008: saving model to batch6.3_008_0.1412.hdf5
Epoch 9/100
163587/163587 [==============================] - 193167s 1s/step - loss: 0.0190 - acc: 0.9939 - val_loss: 0.1204 - val_acc: 0.9710

Epoch 00009: saving model to batch6.3_009_0.1204.hdf5
Epoch 10/100
150682/163587 [==========================>...] - ETA: 4:24:12 - loss: 0.0182 - acc: 0.9942
</pre>