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
