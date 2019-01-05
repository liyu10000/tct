## Finetune Xception

### folders
 - batch6.1_bmp_hls_half_train: use cells from batch6.1, half-size pad with *black* borders, aligned to size 299x299, saved in bmp format. 

### training
1. train1
 - _dataset_: batch6.2, half-sized and pad with black border, all cells aligned to 299x299. Training data are quadrupled by rotating at 90, 180, 270 degrees. Dataset contains three parts: A) original data. B) data with HLS_L = [0.7], HLS_S = [0.4, 0.5]. C) data with HLS_L = [0.5], HLS_S = [0.4, 0.5].
 - _model_: used default Xception model
 - _weights_: used weights trained on batch6.1_bmp_hls_half_train (train6, epoch 010)
 - _init_lr_: 0.002
 - _lr_decay_: 0.5
 - _best_: epoch 
 
<pre>
Found 1601772 images belonging to 21 classes.
Found 44457 images belonging to 21 classes.
Epoch 1/1
12514/12514 [==============================] - 27785s 2s/step - loss: 0.3620 - acc: 0.9124 - val_loss: 0.2068 - val_acc: 0.9420

Found 1601772 images belonging to 21 classes.
Found 44457 images belonging to 21 classes.
Epoch 1/100
25028/25028 [==============================] - 26721s 1s/step - loss: 0.1183 - acc: 0.9597 - val_loss: 0.0969 - val_acc: 0.9671

Epoch 00001: saving model to weights_001_0.0969.hdf5
Epoch 2/100
25028/25028 [==============================] - 26614s 1s/step - loss: 0.1010 - acc: 0.9653 - val_loss: 0.0949 - val_acc: 0.9672

Epoch 00002: saving model to weights_002_0.0949.hdf5
Epoch 3/100
25028/25028 [==============================] - 27910s 1s/step - loss: 0.0976 - acc: 0.9664 - val_loss: 0.0924 - val_acc: 0.9677

Epoch 00003: saving model to weights_003_0.0924.hdf5

Found 1601772 images belonging to 21 classes.
Found 44457 images belonging to 21 classes.
Epoch 4/100
25028/25028 [==============================] - 30714s 1s/step - loss: 0.0793 - acc: 0.9719 - val_loss: 0.0885 - val_acc: 0.9690

Epoch 00004: saving model to weights_004_0.0885.hdf5
Epoch 5/100
25028/25028 [==============================] - 25823s 1s/step - loss: 0.0749 - acc: 0.9733 - val_loss: 0.0885 - val_acc: 0.9684

Epoch 00005: saving model to weights_005_0.0885.hdf5

(log of epoch 6 to 8 is lost)
</pre>
