## Finetune Yolov3
Finetune yolov3 training on TCT project: by the means of changing the lightness and saturation channels of images, we hope to enhance the generalization property of yolov3 model.

### training
1. train1
 - _dataset_: used data batch6. Firstly, cut 1216x1216 rois and resize (cv2.pyrDown) to 608x608. Secondly, change l and s (HLS_L=[0.9], HLS_S=[0.4, 0.5]) of each image.
 - _weights_: used weights pretrained on imagenet (darknet53.conv.74).
 - _batch_: 32
 - _subdivisions_: 8
 - _learning_rate_: 0.00025
 
 - _num_classes_: 1
 - _final_steps_: 152000
 

2. train2
 - _dataset_: used data batch6. From 1216 to 608. The data contains two parts: one part is the same with train1; the other part has the same images but with original l and s.
 - _weights_: used weights trained on train1: hls09_kmeans15_152000.weights
 - _batch_: 64
 - _subdivisions_: 16
 - _learning_rate_: 0.00025
 
 - _num_classes_: 1
 - _final_steps_: 200000
 

3. train3
 - _dataset_: used data batch6. From 1216 to 608. The data contains three parts: one part is the same with train1; the other part has the same images but with original l and s; the third part rotates (90/180/270) the original images. So the dataset is five times the size of train1.
 - _weights_: used weights trained on train2: train2.backup
 - _batch_: 64
 - _subdivisions_: 16
 - _learning_rate_: 0.00025
 
 - _num_classes_: 11
 - _final_steps_: 600000


4. train4
 - _dataset_: used data batch6.1. The data is newly made: we cut positive cells and negative background images out of training wsis, and cut negative cells out of negative wsis; on negative background image, first put a random number (200~500 at most) of negative cells and then put one positive cell, with three more rotations, at random position.
 - _weights_: used weights pretrained on imagenet (darknet53.conv.74)
 - _batch_: 64
 - _subdivisions_: 16
 - _learning_rate_: 0.0005

 - _num_classes_: 11
 - _final_steps_: 100000


5. train5
 - _dataset_: used data batch6.1. The data is newly made: we cut positive cells and negative background images out of training wsis; on negative background image, we put one positive cell, with three more rotations, at random position.
 - _weights_: used weights pretrained on imagenet (darknet53.conv.74)
 - _batch_: 64
 - _subdivisions_: 16
 - _learning_rate_: 0.00025

 - _num_classes_: 11
 - _final_steps_: 100000


6. train6
 - _dataset_: used data batch6.1. The data is newly made: we cut positive cells and negative background images out of training wsis, and cut negative cells out of negative wsis; on negative background image, first put a random number (1~6 at most) of negative cells and then put one positive cell, with three more rotations, at random position.
 - _weights_: used weights pretrained on imagenet (darknet53.conv.74)
 - _batch_: 64
 - _subdivisions_: 16
 - _learning_rate_: 0.00025

 - _num_classes_: 11
 - _final_steps_: 100000