import os

result_dir = "results"
classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC", "AGC1", "AGC2", "ADC", "EC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS"]
#classes = ["class0", "class1", "class2", "class3", "class4", "class5"]

results_file_list = os.listdir(result_dir)
dict_class_file = {}
dict_class_predict_info = {}
dict_class_pic_box_info = {}

for file_name in results_file_list:
    for class_name in classes:
        if (-1 != file_name.find(class_name)):
            dict_class_file[class_name] = file_name

for class_name in dict_class_file:
    file_name = dict_class_file[class_name]
    file_path = result_dir + "/" +file_name
    with open(file_path) as file_object:
        predict_info = file_object.read()
    dict_class_predict_info[class_name] = predict_info
    
for class_name in classes:
    all_predict_info = dict_class_predict_info[class_name].split("\n")
    dict_pic_box_info = {}
    for predict_info in all_predict_info:
        predict_info_list = predict_info.split(" ")
        if (len(predict_info_list) == 6):
            box_info = predict_info_list[1] + " " + predict_info_list[2] + " " + \
                       predict_info_list[3] + " " + predict_info_list[4] + " " + \
                       predict_info_list[5]
            pic_box = []
            pic_box.append(box_info)
            pic_box.append(box_info)
            if (True == (predict_info_list[0] in dict_pic_box_info)):
                temp_pic_box = dict_pic_box_info[predict_info_list[0]]
                temp_pic_box.append(box_info)
                dict_pic_box_info[predict_info_list[0]] = temp_pic_box
            else:
                dict_pic_box_info[predict_info_list[0]] = pic_box   
    dict_class_pic_box_info[class_name] = dict_pic_box_info
    
    
dict_pic_info = {}
dict_class_info = {}

for index, class_name in enumerate(classes):
    dict_pic_box = dict_class_pic_box_info[class_name]
    for pic_name in dict_pic_box:
        class_box_list = dict_pic_box[pic_name]
        for i, class_box in enumerate(class_box_list):
            class_box_list[i] = str(index) + " " + class_box_list[i]
        if (False == (pic_name in dict_pic_info)):
            dict_pic_info[pic_name] = class_box_list
        else:
            dict_pic_info[pic_name] = dict_pic_info[pic_name] + class_box_list

#print(dict_pic_info)
# This format is "PIC:['CLASS DET X1 Y1 X2 Y2', 'CLASS DET X1 Y1 X2 Y2']" 
# dict_pic_info


validata_dir = "../tct_data608_0716_14classes_rotated/validate"
validata_file_list = os.listdir(validata_dir)

validate_txt_file_set = set()
for file_name in validata_file_list:
    common_name = file_name.split(".")[0]
    validate_txt_file_set.add(common_name)

dict_pic_label_box_info = {}

for file_name in validate_txt_file_set:
    file_path = validata_dir + "/" + file_name + ".txt"
    with open(file_path) as file_object:
        lebel_info = file_object.read()
    lebel_info = lebel_info.split("\n")[:-1]
    dict_pic_label_box_info[file_name] = lebel_info
    
#print(dict_pic_label_box_info)
# This format is "PIC:['CLASS X Y W H', 'CLASS X Y W H']" 
#dict_pic_label_box_info

def cal_IOU(Reframe,GTframe):
    """
    自定义函数，计算两矩形 IOU，传入为均为矩形对角线，（x,y）  坐标。
    """
    x1 = Reframe[0]
    y1 = Reframe[1]
    width1 = Reframe[2]-Reframe[0]
    height1 = Reframe[3]-Reframe[1]

    x2 = GTframe[0]
    y2 = GTframe[1]
    width2 = GTframe[2]-GTframe[0]
    height2 = GTframe[3]-GTframe[1]

    endx = max(x1+width1,x2+width2)
    startx = min(x1,x2)
    width = width1+width2-(endx-startx)

    endy = max(y1+height1,y2+height2)
    starty = min(y1,y2)
    height = height1+height2-(endy-starty)

    if width <=0 or height <= 0:
        ratio = 0 # 重叠率为 0 
    else:
        Area = width*height # 两矩形相交面积
        Area1 = width1*height1
        Area2 = width2*height2
        ratio = Area*1./(Area1+Area2-Area)
    # return IOU
    return ratio,Reframe,GTframe

# yolo label like x,y,w,h
# result like x1,y1,x2,y2
def trans_yolo_label(txt_label):
    x = txt_label[0] * 1216
    y = txt_label[1] * 1216
    w = txt_label[2] * 1216
    h = txt_label[3] * 1216
    
    x1 = x - (w / 2)
    y1 = y - (h / 2)
    x2 = x + (w / 2)
    y2 = y + (h / 2)
    
    return([x1, y1, x2, y2])

def trans_str_2_numlist(num_str):
    num_str_list = num_str.split(" ")
    num_list = []
    for i, num_str in enumerate(num_str_list):
        if i == 0:
            num_list.append(int(num_str)) 
        else:
            num_list.append(float(num_str)) 
    return num_list

def trans_strinfo_label(str_info):
    info_list = []
    for str_single_box in str_info:
        info = trans_str_2_numlist(str_single_box)
        info[1:] = trans_yolo_label(info[1:])
        info_list.append(info)
        
    return info_list

def trans_strinfo_pediction(str_info):
    info_list = []
    for str_single_box in str_info:
        info_list.append(trans_str_2_numlist(str_single_box))
    return info_list

def delele_same_predictions(predictions):
    new_predictions = []
    for prediction in predictions:
        if prediction not in new_predictions:
            new_predictions.append(prediction)
    return new_predictions

def cal_recall_count(label_object_count, prediction_object_count, labels_in_single_pic, predictions_in_single_pic):
    for label_object in labels_in_single_pic:
        label_object_count[label_object[0]] += 1

#    for prediction_object in predictions_in_single_pic:
#        if( prediction_object[1] > 0.05):
#            max_IOU = 0
#            for label_object in labels_in_single_pic:
#                if (prediction_object[0] == label_object[0]):
#                    IOU = cal_IOU(prediction_object[2:],label_object[1:])
#                    if (IOU[0] > max_IOU):
#                        max_IOU = IOU[0]
#            if (max_IOU > 0.3):
#                prediction_object_count[prediction_object[0]] += 1

    for label_object in labels_in_single_pic:
        max_IOU = 0
        for prediction_object in predictions_in_single_pic:
            #if (prediction_object[0] == label_object[0]):
            if (1):
                if( prediction_object[1] > 0.05):
                    IOU = cal_IOU(prediction_object[2:],label_object[1:])
                    if (IOU[0] > max_IOU):
                        max_IOU = IOU[0]
        if (max_IOU > 0.3):
            prediction_object_count[label_object[0]] += 1
        

# test 200,200,400,400 & 300,300,500,500
# 200,200,400,400 use yolo is (300,300,200,200) or (0.2467,0.2467,0.1645,0.1645)
cal_IOU([200, 200, 400, 400], [300, 300, 500, 500])
trans_yolo_label([0.2467, 0.2467, 0.1645, 0.1645])


#dict_pic_info
#dict_pic_label_box_info

label_object_count = [0 for i in range(len(classes))]
prediction_object_count = [0 for i in range(len(classes))]
recalls = [0 for i in range(len(classes))]

for pic_name in dict_pic_info:
    predictions_in_single_pic = trans_strinfo_pediction(dict_pic_info[pic_name])
    labels_in_single_pic = trans_strinfo_label(dict_pic_label_box_info[pic_name])
    predictions_in_single_pic = delele_same_predictions(predictions_in_single_pic)
    cal_recall_count(label_object_count, prediction_object_count, 
                     labels_in_single_pic, predictions_in_single_pic)

for i, recall in enumerate(recalls):
    if (label_object_count[i] != 0):
        recalls[i] = prediction_object_count[i] / label_object_count[i]
    else:
        recalls[i] = 0
        
for i, class_name in enumerate(classes):
    print(class_name + "\t" + ":" + 
          "\t" + str(prediction_object_count[i]) + "/" +
          str(label_object_count[i]) + "      "
          "\t" + "recall" + ":" + "\t" + str(recalls[i]))
          
