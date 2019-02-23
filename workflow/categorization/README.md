## Image pre-classification
This CNN model serves to classify and clarify which category the input image belongs to, before cell detection. It will contribute to the confirmation of detected cells, and save time to some extent.

### Training
1. train1
 - _dataset_: The data comes from resizing of darknet/train13. It was first resized to 299x299 as xception input but was soon found to be too slow at training. After further resizing to 224x224, it was made into lmdb database for caffe.
 - _weights_: resnet50_cvgj_iter_320000.caffemodel
