import os
from prediction_evaluate import *

result_dir = "../results"
validate_dir = "../../tct_data608_0716_14classes_rotated/validate"
classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC", "AGC1", "AGC2", 
          "ADC", "EC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS"]
# classes = ["ASCUS"]
# classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]

dict_pic_info = get_predictions_result(result_dir, classes)
dict_pic_label_box_info = get_labels(validate_dir, classes)

print(len(dict_pic_info))
print(len(dict_pic_label_box_info))

det = 0.05
iou = 0.3
img_size = 608
all_prediction_object_count, prediction_object_count, label_object_count,\
recalls, accurates = cal_evaluate(dict_pic_info, dict_pic_label_box_info,
                                  classes, det, iou, img_size)
print_evaluate(classes,
               all_prediction_object_count, 
               prediction_object_count, 
               label_object_count,
               recalls, 
               accurates)