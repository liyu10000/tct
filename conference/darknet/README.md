## Finetune Yolov3
Finetune yolov3 training on TCT project: by the means of changing the lightness and saturation channels of images, we hope to enhance the generalization property of yolov3 model.

### training
1. train1
 - _dataset_: used data batch6. Firstly, cut 1216x1216 rois and resize (cv2.pyrDown) to 608x608. Secondly, change l and s (HLS_L=[0.9], HLS_S=[0.4, 0.5]) of each image.
 - _weights_: used weights pretrained on imagenet (darknet53.conv.74).
 - _batch_: 64
 - _subdivisions_: 16
 - _learning_rate_: 0.00025