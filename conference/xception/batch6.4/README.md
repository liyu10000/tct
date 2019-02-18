## Finetune Xception

### folders
 - batch6.4: use cells from batch6.4, half-size pad with *black* borders, aligned to size 299x299, saved in bmp format. 

### training
1. train1
 - _dataset_: batch6.4 (partly deteled batch6.3 + newly added), half-sized and pad with black border, all cells aligned to 299x299. Training data are quadrupled by rotating at 90, 180, 270 degrees. Dataset contains three parts: A) original data. B) data with HLS_L = [0.7], HLS_S = [0.4, 0.5]. C) data with HLS_L = [0.5], HLS_S = [0.4, 0.5].
 - _model_: used default Xception model
 - _weights_: used weights trained on batch6.3 (train6.3, epoch 009)
 - _init_lr_: 0.002
 - _lr_decay_: 0.5
 - _best_: epoch 012
 
<pre>
Found 1729032 images belonging to 21 classes.
Found 48000 images belonging to 21 classes.
Epoch 1/100
27017/27017 [==============================] - 13043s 483ms/step - loss: 0.1023 - acc: 0.9651 - val_loss: 0.1062 - val_acc: 0.9631

Epoch 00001: saving model to batch6.4_001_0.1062.hdf5
Epoch 2/100
27017/27017 [==============================] - 12988s 481ms/step - loss: 0.0928 - acc: 0.9682 - val_loss: 0.1043 - val_acc: 0.9638

Epoch 00002: saving model to batch6.4_002_0.1043.hdf5
Epoch 3/100
27017/27017 [==============================] - 12994s 481ms/step - loss: 0.0907 - acc: 0.9687 - val_loss: 0.1037 - val_acc: 0.9637

Epoch 00003: saving model to batch6.4_003_0.1037.hdf5
Epoch 4/100
27017/27017 [==============================] - 13004s 481ms/step - loss: 0.0893 - acc: 0.9693 - val_loss: 0.1030 - val_acc: 0.9641

Epoch 00004: saving model to batch6.4_004_0.1030.hdf5
Epoch 5/100
27017/27017 [==============================] - 13024s 482ms/step - loss: 0.0881 - acc: 0.9697 - val_loss: 0.1029 - val_acc: 0.9640

Epoch 00005: saving model to batch6.4_005_0.1029.hdf5
Epoch 6/100
27017/27017 [==============================] - 13027s 482ms/step - loss: 0.0876 - acc: 0.9698 - val_loss: 0.1041 - val_acc: 0.9636

Epoch 00006: saving model to batch6.4_006_0.1041.hdf5
Epoch 7/100
27017/27017 [==============================] - 13012s 482ms/step - loss: 0.0869 - acc: 0.9700 - val_loss: 0.1033 - val_acc: 0.9641

Epoch 00007: saving model to batch6.4_007_0.1033.hdf5
Epoch 8/100
27017/27017 [==============================] - 12999s 481ms/step - loss: 0.0871 - acc: 0.9699 - val_loss: 0.1038 - val_acc: 0.9637

Epoch 00008: saving model to batch6.4_008_0.1038.hdf5
Epoch 9/100
27017/27017 [==============================] - 12975s 480ms/step - loss: 0.0871 - acc: 0.9700 - val_loss: 0.1031 - val_acc: 0.9636

Epoch 00009: saving model to batch6.4_009_0.1031.hdf5
Epoch 10/100
27017/27017 [==============================] - 12958s 480ms/step - loss: 0.0873 - acc: 0.9701 - val_loss: 0.1043 - val_acc: 0.9637

Epoch 00010: saving model to batch6.4_010_0.1043.hdf5
Epoch 11/100
27017/27017 [==============================] - 12951s 479ms/step - loss: 0.0872 - acc: 0.9700 - val_loss: 0.1039 - val_acc: 0.9636

Epoch 00011: saving model to batch6.4_011_0.1039.hdf5
Epoch 12/100
 1750/27017 [>.............................] - ETA: 3:19:49 - loss: 0.0866 - acc: 0.9702
</pre>

2. train2
 - _dataset_: batch6.3 (partly deteled batch6.3), half-sized and pad with black border, all cells aligned to 299x299. Training data are quadrupled by rotating at 90, 180, 270 degrees. Dataset contains three parts: A) original data. B) data with HLS_L = [0.7], HLS_S = [0.4, 0.5]. C) data with HLS_L = [0.5], HLS_S = [0.4, 0.5].
 - _model_: used default Xception model
 - _weights_: used weights trained on batch6.3 (train6.3, epoch 009)
 - _init_lr_: 0.002
 - _lr_decay_: 0.5
 - _best_: epoch 007
 
 <pre>
 Found 1570764 images belonging to 21 classes.
Found 43605 images belonging to 21 classes.
Epoch 1/100
24544/24544 [==============================] - 11759s 479ms/step - loss: 0.0599 - acc: 0.9795 - val_loss: 0.0660 - val_acc: 0.9771

Epoch 00001: saving model to batch6.4_001_0.0660.hdf5
Epoch 2/100
24544/24544 [==============================] - 11754s 479ms/step - loss: 0.0566 - acc: 0.9804 - val_loss: 0.0660 - val_acc: 0.9778

Epoch 00002: saving model to batch6.4_002_0.0660.hdf5
Epoch 3/100
24544/24544 [==============================] - 11766s 479ms/step - loss: 0.0560 - acc: 0.9806 - val_loss: 0.0667 - val_acc: 0.9772

Epoch 00003: saving model to batch6.4_003_0.0667.hdf5
Epoch 4/100
24544/24544 [==============================] - 11790s 480ms/step - loss: 0.0555 - acc: 0.9809 - val_loss: 0.0657 - val_acc: 0.9779

Epoch 00004: saving model to batch6.4_004_0.0657.hdf5
Epoch 5/100
24544/24544 [==============================] - 11801s 481ms/step - loss: 0.0554 - acc: 0.9809 - val_loss: 0.0647 - val_acc: 0.9780

Epoch 00005: saving model to batch6.4_005_0.0647.hdf5
Epoch 6/100
24544/24544 [==============================] - 11794s 481ms/step - loss: 0.0555 - acc: 0.9808 - val_loss: 0.0656 - val_acc: 0.9775

Epoch 00006: saving model to batch6.4_006_0.0656.hdf5
Epoch 7/100
24544/24544 [==============================] - 11797s 481ms/step - loss: 0.0554 - acc: 0.9809 - val_loss: 0.0655 - val_acc: 0.9777

Epoch 00007: saving model to batch6.4_007_0.0655.hdf5
Epoch 8/100
  791/24544 [..............................] - ETA: 3:08:06 - loss: 0.0540 - acc: 0.9819
 </pre>