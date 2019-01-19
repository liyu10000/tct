## Finetune Xception

### folders
 - batch6.2: use cells from batch6.2, half-size pad with *black* borders, aligned to size 299x299, saved in bmp format. 

### training
1. train1
 - _dataset_: batch6.3, half-sized and pad with black border, all cells aligned to 299x299. Training data are quadrupled by rotating at 90, 180, 270 degrees. Dataset contains three parts: A) original data. B) data with HLS_L = [0.7], HLS_S = [0.4, 0.5]. C) data with HLS_L = [0.5], HLS_S = [0.4, 0.5].
 - _model_: used default Xception model
 - _weights_: used weights trained on batch6.2 (train6.2, epoch 008)
 - _init_lr_: 0.002
 - _lr_decay_: 0.5
 - _best_: epoch 
 
<pre>
Found 1768236 images belonging to 21 classes.
Found 49086 images belonging to 21 classes.
Epoch 1/100
27629/27629 [==============================] - 30166s 1s/step - loss: 0.0844 - acc: 0.9697 - val_loss: 0.0805 - val_acc: 0.9716

Epoch 00001: saving model to batch6.3_001_0.0805.hdf5
Epoch 2/100
27629/27629 [==============================] - 29541s 1s/step - loss: 0.0773 - acc: 0.9722 - val_loss: 0.0786 - val_acc: 0.9721

Epoch 00002: saving model to batch6.3_002_0.0786.hdf5
Epoch 3/100
27629/27629 [==============================] - 29532s 1s/step - loss: 0.0754 - acc: 0.9732 - val_loss: 0.0772 - val_acc: 0.9728

Epoch 00003: saving model to batch6.3_003_0.0772.hdf5
Epoch 4/100
14418/27629 [==============>...............] - ETA: 3:44:19 - loss: 0.0744 - acc: 0.9732

(log of epoch 4 to 9 is lost)
</pre>
