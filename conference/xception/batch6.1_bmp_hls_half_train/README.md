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
 - _best_: epoch 010

<pre>
Found 1370376 images belonging to 20 classes.
Found 38043 images belonging to 20 classes.
Epoch 1/100
21413/21413 [==============================] - 20233s 945ms/step - loss: 0.0899 - acc: 0.9670 - val_loss: 0.0786 - val_acc: 0.9733

Epoch 3/100
21413/21413 [==============================] - 16555s 773ms/step - loss: 0.0707 - acc: 0.9739 - val_loss: 0.0722 - val_acc: 0.9747

Epoch 00003: saving model to weights_003_0.0722.hdf5
Epoch 4/100
21413/21413 [==============================] - 17785s 831ms/step - loss: 0.0669 - acc: 0.9753 - val_loss: 0.0711 - val_acc: 0.9757

Epoch 00004: saving model to weights_004_0.0711.hdf5
Epoch 5/100
21413/21413 [==============================] - 24821s 1s/step - loss: 0.0663 - acc: 0.9757 - val_loss: 0.0705 - val_acc: 0.9754

Epoch 00005: saving model to weights_005_0.0705.hdf5
Epoch 6/100
21413/21413 [==============================] - 27531s 1s/step - loss: 0.0649 - acc: 0.9759 - val_loss: 0.0690 - val_acc: 0.9761

Epoch 00006: saving model to weights_006_0.0690.hdf5
Epoch 7/100
21413/21413 [==============================] - 20144s 941ms/step - loss: 0.0648 - acc: 0.9761 - val_loss: 0.0701 - val_acc: 0.9753

Epoch 00007: saving model to weights_007_0.0701.hdf5
Epoch 8/100
21413/21413 [==============================] - 17688s 826ms/step - loss: 0.0643 - acc: 0.9764 - val_loss: 0.0702 - val_acc: 0.9755

Epoch 00008: saving model to weights_008_0.0702.hdf5
Epoch 9/100
21413/21413 [==============================] - 23579s 1s/step - loss: 0.0641 - acc: 0.9762 - val_loss: 0.0707 - val_acc: 0.9752

Epoch 00009: saving model to weights_009_0.0707.hdf5
Epoch 10/100
21413/21413 [==============================] - 26716s 1s/step - loss: 0.0642 - acc: 0.9763 - val_loss: 0.0698 - val_acc: 0.9756

Epoch 00010: saving model to weights_010_0.0698.hdf5
Epoch 11/100
21413/21413 [==============================] - 25590s 1s/step - loss: 0.0642 - acc: 0.9763 - val_loss: 0.0702 - val_acc: 0.9755

Epoch 00011: saving model to weights_011_0.0702.hdf5
Epoch 12/100
21413/21413 [==============================] - 19784s 924ms/step - loss: 0.0643 - acc: 0.9762 - val_loss: 0.0697 - val_acc: 0.9757

Epoch 00012: saving model to weights_012_0.0697.hdf5
Epoch 13/100
21413/21413 [==============================] - 23147s 1s/step - loss: 0.0640 - acc: 0.9763 - val_loss: 0.0704 - val_acc: 0.9756

Epoch 00013: saving model to weights_013_0.0704.hdf5
</pre>