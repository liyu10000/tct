## Finetune Xception

### folders
 - batch6.1_bmp_hls_half_train: use cells from batch6.1, half-size pad with *black* borders, aligned to size 299x299, saved in bmp format. 

### training
1. train1
 - _dataset_: batch6.1, half-sized and pad with black border, all cells aligned to 299x299. Training data are quadrupled by rotating at 90, 180, 270 degrees. Dataset contains three parts: A) original data. B) data with HLS_L = [0.7], HLS_S = [0.4, 0.5]. C) data with HLS_L = [0.5], HLS_S = [0.4, 0.5].
 - _model_: used default Xception model
 - _weights_: used weights trained on batch6.1_hls_half_train (train6, epoch 004)
 - _init_lr_: 0.001
 - _lr_decay_: 0.5

<pre>
Found 1370376 images belonging to 20 classes.
Found 38043 images belonging to 20 classes.
Epoch 1/100
21413/21413 [==============================] - 20233s 945ms/step - loss: 0.0899 - acc: 0.9670 - val_loss: 0.0786 - val_acc: 0.9733
</pre>