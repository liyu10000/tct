## Finetune Xception

### folders
 - batch6_half_train: use cells from batch6, half-size and pad with black borders, aligned to size 299x299. Use original Xception model for training.
 - batch6.1_hls_half_train: use cells from batch6.1, half-size and pad with white borders, aligned to size 299x299. Modified original model.

### training
 - train1
_dataset_: batch6.1, half-sized and pad with white border, all cells aligned to 299x299. read from jpg, save to jpg, with opencv. training data are quadrupled by rotating at 90, 180, 270 degrees.
_model_: used default Xception model
_weights_: used weights trained on dataset batch 6

 - train2
_dataset_: the same with train1
_model_: added two layers after base model (Conv2D and BatchNormalization)
_weights_: used weights trained on dataset batch 6

 - train3
_dataset_: the same with train1
_model_: added two layers after base model (Conv2D and BatchNormalization)
_weights_: used pretrained weights on imagenet

 - train4
_dataset_: the same with train1
_model_: used default Xception model
_weights_: used weights trained from train1, epoch 003
_init_lr_: 0.005

Found 456792 images belonging to 20 classes.
Found 12681 images belonging to 20 classes.
Epoch 4/150
7138/7138 [==============================] - 4247s 595ms/step - loss: 0.1646 - acc: 0.9416 - val_loss: 0.1472 - val_acc: 0.9492

Epoch 00004: saving model to weights_004_0.1472.hdf5
Epoch 5/150
7138/7138 [==============================] - 4168s 584ms/step - loss: 0.1378 - acc: 0.9498 - val_loss: 0.1439 - val_acc: 0.9521

Epoch 00005: saving model to weights_005_0.1439.hdf5
Epoch 6/150
7138/7138 [==============================] - 4132s 579ms/step - loss: 0.1294 - acc: 0.9525 - val_loss: 0.1433 - val_acc: 0.9543

Epoch 00006: saving model to weights_006_0.1433.hdf5
Epoch 7/150
7138/7138 [==============================] - 4171s 584ms/step - loss: 0.1242 - acc: 0.9544 - val_loss: 0.1190 - val_acc: 0.9579

Epoch 00007: saving model to weights_007_0.1190.hdf5
Epoch 8/150
7138/7138 [==============================] - 4210s 590ms/step - loss: 0.1198 - acc: 0.9556 - val_loss: 0.1537 - val_acc: 0.9542

Epoch 00008: saving model to weights_008_0.1537.hdf5
Epoch 9/150
7138/7138 [==============================] - 4163s 583ms/step - loss: 0.1176 - acc: 0.9564 - val_loss: 0.1396 - val_acc: 0.9563

Epoch 00009: saving model to weights_009_0.1396.hdf5
Epoch 10/150
7138/7138 [==============================] - 4164s 583ms/step - loss: 0.1173 - acc: 0.9567 - val_loss: 0.1299 - val_acc: 0.9568

Epoch 00010: saving model to weights_010_0.1299.hdf5
Epoch 11/150
7138/7138 [==============================] - 4156s 582ms/step - loss: 0.1170 - acc: 0.9566 - val_loss: 0.1257 - val_acc: 0.9578

Epoch 00011: saving model to weights_011_0.1257.hdf5
Epoch 12/150
7138/7138 [==============================] - 4163s 583ms/step - loss: 0.1168 - acc: 0.9565 - val_loss: 0.1276 - val_acc: 0.9573

Epoch 00012: saving model to weights_012_0.1276.hdf5
Epoch 13/150
7138/7138 [==============================] - 4160s 583ms/step - loss: 0.1161 - acc: 0.9568 - val_loss: 0.1285 - val_acc: 0.9575

Epoch 00013: saving model to weights_013_0.1285.hdf5
Epoch 14/150
7138/7138 [==============================] - 4221s 591ms/step - loss: 0.1170 - acc: 0.9567 - val_loss: 0.1516 - val_acc: 0.9547

Epoch 00014: saving model to weights_014_0.1516.hdf5
Epoch 15/150
7138/7138 [==============================] - 4174s 585ms/step - loss: 0.1172 - acc: 0.9566 - val_loss: 0.1442 - val_acc: 0.9554

Epoch 00015: saving model to weights_015_0.1442.hdf5
Epoch 16/150
7138/7138 [==============================] - 4190s 587ms/step - loss: 0.1157 - acc: 0.9570 - val_loss: 0.1305 - val_acc: 0.9566

Epoch 00016: saving model to weights_016_0.1305.hdf5
Epoch 17/150
7138/7138 [==============================] - 4236s 593ms/step - loss: 0.1160 - acc: 0.9572 - val_loss: 0.1281 - val_acc: 0.9571

Epoch 00017: saving model to weights_017_0.1281.hdf5


 - train5
_dataset_: two parts: one part is from train1; the other part has the same number and source as train1 dataset, except that all images's l and s are enhanced.
_model_: used default Xception model
_weights_: used weights trained from train4, epoch 017
_init_lr_: 0.001 at epochs 1-3, 0.0005 at epochs 4-9, 0.005 at epochs 10-16
_lr_decay_: 0.5 at epochs 1-3, 0.6 at epochs 4-9, 0.6 at epochs 10-16

Found 913584 images belonging to 20 classes.
Found 25362 images belonging to 20 classes.
Epoch 1/100
14275/14275 [==============================] - 8182s 573ms/step - loss: 0.1901 - acc: 0.9333 - val_loss: 0.2181 - val_acc: 0.9384

Epoch 00001: saving model to weights_001_0.2181.hdf5
Epoch 2/100
14275/14275 [==============================] - 8064s 565ms/step - loss: 0.1764 - acc: 0.9369 - val_loss: 0.2066 - val_acc: 0.9402

Epoch 00002: saving model to weights_002_0.2066.hdf5
Epoch 3/100
14275/14275 [==============================] - 8172s 572ms/step - loss: 0.1730 - acc: 0.9378 - val_loss: 0.2411 - val_acc: 0.9379

Found 913584 images belonging to 20 classes.
Found 25362 images belonging to 20 classes.
Epoch 4/100
14275/14275 [==============================] - 8667s 607ms/step - loss: 0.1692 - acc: 0.9390 - val_loss: 0.2138 - val_acc: 0.9407

Epoch 00004: saving model to weights_004_0.2138.hdf5
Epoch 5/100
14275/14275 [==============================] - 8623s 604ms/step - loss: 0.1662 - acc: 0.9401 - val_loss: 0.1993 - val_acc: 0.9421

Epoch 00005: saving model to weights_005_0.1993.hdf5
Epoch 6/100
14275/14275 [==============================] - 8572s 600ms/step - loss: 0.1650 - acc: 0.9403 - val_loss: 0.1954 - val_acc: 0.9427

Epoch 00006: saving model to weights_006_0.1954.hdf5
Epoch 7/100
14275/14275 [==============================] - 8623s 604ms/step - loss: 0.1642 - acc: 0.9409 - val_loss: 0.2053 - val_acc: 0.9424

Epoch 00007: saving model to weights_007_0.2053.hdf5
Epoch 8/100
14275/14275 [==============================] - 8600s 602ms/step - loss: 0.1643 - acc: 0.9407 - val_loss: 0.2091 - val_acc: 0.9418

Epoch 00008: saving model to weights_008_0.2091.hdf5
Epoch 9/100
14275/14275 [==============================] - 8652s 606ms/step - loss: 0.1636 - acc: 0.9411 - val_loss: 0.2320 - val_acc: 0.9395

Epoch 00009: saving model to weights_009_0.2320.hdf5

Found 913584 images belonging to 20 classes.
Found 25362 images belonging to 20 classes.
Epoch 10/100
14274/14275 [============================>.] - ETA: 0s - loss: 0.1535 - acc: 0.9441
14275/14275 [==============================] - 8322s 583ms/step - loss: 0.1535 - acc: 0.9441 - val_loss: 0.2314 - val_acc: 0.9447

Epoch 00004: saving model to weights_004_0.2314.hdf5
Epoch 11/100
14275/14275 [==============================] - 8505s 596ms/step - loss: 0.1403 - acc: 0.9480 - val_loss: 0.3009 - val_acc: 0.9394

Epoch 00005: saving model to weights_005_0.3009.hdf5
Epoch 12/100
14275/14275 [==============================] - 8269s 579ms/step - loss: 0.1373 - acc: 0.9492 - val_loss: 0.2668 - val_acc: 0.9424

Epoch 00006: saving model to weights_006_0.2668.hdf5
Epoch 13/100
14275/14275 [==============================] - 8418s 590ms/step - loss: 0.1351 - acc: 0.9498 - val_loss: 0.2899 - val_acc: 0.9401

Epoch 00007: saving model to weights_007_0.2899.hdf5
Epoch 14/100
14274/14275 [============================>.] - ETA: 0s - loss: 0.1345 - acc: 0.9502
Epoch 00007: saving model to weights_007_0.2899.hdf5
14275/14275 [==============================] - 8172s 572ms/step - loss: 0.1345 - acc: 0.9502 - val_loss: 0.3299 - val_acc: 0.9377

Epoch 00008: saving model to weights_008_0.3299.hdf5
Epoch 15/100
14275/14275 [==============================] - 8271s 579ms/step - loss: 0.1342 - acc: 0.9502 - val_loss: 0.2658 - val_acc: 0.9422

Epoch 00009: saving model to weights_009_0.2658.hdf5
Epoch 16/100
14275/14275 [==============================] - 8390s 588ms/step - loss: 0.1343 - acc: 0.9503 - val_loss: 0.2750 - val_acc: 0.9412

Epoch 00010: saving model to weights_010_0.2750.hdf5