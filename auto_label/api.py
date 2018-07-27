#this will be one-stop service: from tif to classified images for inspection
import os
import shutil
import numpy as np
from asap_to_jpg import asap_to_image
from segment import gen_txt_for_dir, segment
from prediction_evaluate import get_predictions_result
from prediction_convert import prediction_convert
from jpg_to_cell import get_cells
from Xception_classify import xception_init, xception_predict
from Xception_convert import xception_convert
from utils import scan_files, scan_subdirs, copy_files, remove_files

# cut tif file to 608x608 images. For each tif, it will generate a folder to put 608 images ###########################
input_tif_files = "/home/sakulaki/yolo-yuli/one_stop_test/tif"
output_tif_608s = "/home/sakulaki/yolo-yuli/one_stop_test/608"
#asap_to_image(input_tif_files, output_tif_608s)

# for each tif, run segmentation and classification, generate jpg/xml for labelme #####################################
tif_names = scan_subdirs(output_tif_608s)
for tif_name in tif_names:
    image_path = os.path.join(output_tif_608s, tif_name)
    
    # get the list of 608 image full pathnames ########################################################################
    images = scan_files(image_path)

    # generate txt file for current tif ###############################################################################
    print("[INFO] generate txt for " + tif_name)
    gen_txt_for_dir(images, output_tif_608s, tif_name)

    # run darknet test ################################################################################################
    darknet_path = "/home/sakulaki/yolo-yuli/darknet"
    segment(darknet_path, image_path)
    os.remove(image_path+".txt")

    # evaluate predictions and convert coordinates to xmls ############################################################
    print("[INFO] evaluate predictions and write coordinates into xmls")
    result_dir = os.path.join(darknet_path, "results")
    classes_list = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
    dict_pic_info = get_predictions_result(result_dir, classes_list)
    img_size = 608
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    det = 0.05
    prediction_convert(dict_pic_info, classes_list, img_size, segment_xml_path, det)

    # copy xmls from segment folder to jpg folder, for purpose of cropping images #####################################
    print("[INFO] copy xmls from segment folder to jpg folder")
    xmls = scan_files(segment_xml_path, postfix=".xml")
    for xml in xmls:
        shutil.copy(xml, image_path)
    # copy_files(segment_xml_path, image_path, postfix=".xml")

    # crop cells out of 608 jpgs and save into numpy array, based on predicted xmls ###################################
    print("[INFO] crop cells out of 608 jpgs and save into numpy array, based on xmls")
    classes_dict = {"HSIL":0, "ASCH":0, "LSIL":0, "ASCUS":0, "SCC":0}
    files_list = scan_files(image_path, postfix=".xml")
    size = 299
    cell_numpy, cell_numpy_index = get_cells(files_list, classes_dict, size)
    print(cell_numpy.shape)
    print("segmentation result: ", sorted(classes_dict.items()))

    # delete xmls_segment from jpg folder and copy jpgs to segment folder #############################################
    print("[INFO] delete xmls_segment from jpg folder and copy jpgs to segment folder")
    xmls = scan_files(image_path, postfix=".xml")
    for xml in xmls:
        os.remove(xml)
        jpg = os.path.join(image_path, os.path.basename(os.path.splitext(xml)[0])+".jpg")
        shutil.copy(jpg, segment_xml_path)
    #remove_files(image_path, postfix=".xml")
    
    # run classification ##############################################################################################
    print("[INFO] run classification")   
    model = xception_init("Xception_finetune.h5")
    predictions = xception_predict(cell_numpy, batch_size=20, model=model)
    print(predictions.shape)

    # generate new dict_pic_info mapping ##############################################################################
    print("[INFO] generate new dict_pic_info mapping")
    classes_all = ("ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", 
                   "MC", "RC", "SC", "SCC", "TRI", "VIRUS")
    # segment_in_classify: {class_i:[segment, classify]}
    segment_in_classify = {"ACTINO":[0,0], "ADC":[0,0], "AGC1":[0,0], "AGC2":[0,0], "ASCH":[0,0], "ASCUS":[0,0], 
                           "CC":[0,0], "EC":[0,0], "FUNGI":[0,0], "GEC":[0,0], "HSIL":[0,0], "LSIL":[0,0], "MC":[0,0], 
                           "RC":[0,0], "SC":[0,0], "SCC":[0,0], "TRI":[0,0], "VIRUS":[0,0]} 
    index = 0
    dict_pic_info_all = {}
    for prediction in predictions:
        i = np.argmax(prediction)
        class_i = classes_all[i]
        segment_in_classify[class_i][1] += 1
        if cell_numpy_index[index][1] == class_i:
            segment_in_classify[class_i][0] += 1
            x_y, i_of_x_y = cell_numpy_index[index][0].rsplit("_", 1)
            i_of_x_y = int(i_of_x_y)
            space_i = dict_pic_info[x_y][i_of_x_y].find(" ", 3)
            cell_info = dict_pic_info[x_y][i_of_x_y][:space_i] + " " + str(i) + " " + str(prediction[i]) + dict_pic_info[x_y][i_of_x_y][space_i:]
            if not x_y in dict_pic_info_all:
                dict_pic_info_all[x_y] = [cell_info,]
            else:
                dict_pic_info_all[x_y].append(cell_info)
        index += 1
    print("segment_in_classify: ", sorted(segment_in_classify.items()))

    # generate xmls, based on classification results ##################################################################
    print("[INFO] generate xmls based on classification")
    img_size = 608
    classify_xml_path = os.path.join(output_tif_608s, tif_name+"_classify")
    det = 0.1
    xception_convert(dict_pic_info_all, classes_all, img_size, classify_xml_path, det)

    # copy jpgs from jpg folder to xmls_classify folder ###############################################################
    print("[INFO] copy jpgs from jpg folder to xmls_classify folder")
    xmls = scan_files(classify_xml_path, postfix=".xml")
    for xml in xmls:
        jpg = os.path.join(image_path, os.path.basename(os.path.splitext(xml)[0])+".jpg")
        shutil.copy(jpg, classify_xml_path)