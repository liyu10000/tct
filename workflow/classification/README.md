## Cell Classification

1. train1
 - _dataset_: batch6.4 (full batch6.3 + newly added).
 - _model_: caffe/resnet50


2. train2 tune1
 - _dataset_: batch6.4 (full batch6.3 + newly added).
 - _model_: keras/xception
 - _weights_: pretrained weights on imagenet
 - _init_lr_: 0.005
 - _lr_ctrl_: sgd
 
<pre>
Found 1787040 images belonging to 21 classes.
Found 49608 images belonging to 21 classes.
Epoch 1/1
6981/6981 [==============================] - 6500s 931ms/step - loss: 1.4242 - acc: 0.5717 - val_loss: 3.0761 - val_acc: 0.2191

Found 1787040 images belonging to 21 classes.
Found 49608 images belonging to 21 classes.
Epoch 1/100
13962/13962 [==============================] - 7725s 553ms/step - loss: 0.2188 - acc: 0.9227 - val_loss: 0.1607 - val_acc: 0.9423

Epoch 00001: saving model to batch6.4_001_0.1607.hdf5
Epoch 2/100
13962/13962 [==============================] - 7667s 549ms/step - loss: 0.1240 - acc: 0.9556 - val_loss: 0.1544 - val_acc: 0.9463

Epoch 00002: saving model to batch6.4_002_0.1544.hdf5
Epoch 3/100
13962/13962 [==============================] - 7621s 546ms/step - loss: 0.1048 - acc: 0.9625 - val_loss: 0.1532 - val_acc: 0.9485

Epoch 00003: saving model to batch6.4_003_0.1532.hdf5
Epoch 4/100
13962/13962 [==============================] - 7545s 540ms/step - loss: 0.0910 - acc: 0.9674 - val_loss: 0.1514 - val_acc: 0.9495

Epoch 00004: saving model to batch6.4_004_0.1514.hdf5
Epoch 5/100
13962/13962 [==============================] - 7240s 519ms/step - loss: 0.0814 - acc: 0.9708 - val_loss: 0.1545 - val_acc: 0.9505

Epoch 00005: saving model to batch6.4_005_0.1545.hdf5
Epoch 6/100
13962/13962 [==============================] - 7270s 521ms/step - loss: 0.0743 - acc: 0.9734 - val_loss: 0.1558 - val_acc: 0.9506

Epoch 00006: saving model to batch6.4_006_0.1558.hdf5
Epoch 7/100
13962/13962 [==============================] - 7387s 529ms/step - loss: 0.0685 - acc: 0.9755 - val_loss: 0.1567 - val_acc: 0.9516

Epoch 00007: saving model to batch6.4_007_0.1567.hdf5
Epoch 8/100
13962/13962 [==============================] - 7722s 553ms/step - loss: 0.0634 - acc: 0.9775 - val_loss: 0.1578 - val_acc: 0.9517

Epoch 00008: saving model to batch6.4_008_0.1578.hdf5
Epoch 9/100
13962/13962 [==============================] - 7563s 542ms/step - loss: 0.0625 - acc: 0.9778 - val_loss: 0.1600 - val_acc: 0.9514

Epoch 00009: saving model to batch6.4_009_0.1600.hdf5
Epoch 10/100
13962/13962 [==============================] - 7454s 534ms/step - loss: 0.0622 - acc: 0.9777 - val_loss: 0.1589 - val_acc: 0.9517

Epoch 00010: saving model to batch6.4_010_0.1589.hdf5
Epoch 11/100
13962/13962 [==============================] - 7447s 533ms/step - loss: 0.0618 - acc: 0.9780 - val_loss: 0.1587 - val_acc: 0.9514

Epoch 00011: saving model to batch6.4_011_0.1587.hdf5
Epoch 12/100
13962/13962 [==============================] - 7627s 546ms/step - loss: 0.0616 - acc: 0.9781 - val_loss: 0.1598 - val_acc: 0.9514

Epoch 00012: saving model to batch6.4_012_0.1598.hdf5
Epoch 13/100
13962/13962 [==============================] - 8068s 578ms/step - loss: 0.0617 - acc: 0.9780 - val_loss: 0.1590 - val_acc: 0.9516

Epoch 00013: saving model to batch6.4_013_0.1590.hdf5
Epoch 14/100
  336/13962 [..............................] - ETA: 2:02:43 - loss: 0.0574 - acc: 0.9793
</pre>


3. train2 tune2
 - _dataset_: batch6.4 (full batch6.3 + newly added).
 - _model_: keras/xception
 - _weights_: weights 013 of train2 tune1
 - _init_lr_: adadelta
 - _lr_ctrl_: adadelta
 - _excess_: use aug-on-fly
 
<pre>

</pre>