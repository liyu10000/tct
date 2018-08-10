#this will be one-stop service: from tif to classified images for inspection
import os
import sys
import shutil
import numpy as np
import colorama
from asap_to_jpg import asap_to_image
from segment import gen_txt_for_dir, segment
from prediction_evaluate import get_predictions_result
from prediction_convert import prediction_convert
from jpg_to_cell import get_cells
from Xception_classify import xception_init, xception_predict
from Xception_convert import xception_convert, dict_to_csv
from confusion_matrix import confusion_matrix, generate_xlsx
from xml_to_asap import gen_asap_xml
from utils import scan_files, scan_subdirs, copy_files, remove_files

colorama.init()

# configuration #######################################################################################################
input_tif_files = "/home/sakulaki/yolo-yuli/one_stop_test/yantian_tif"
output_tif_608s = "/home/sakulaki/yolo-yuli/one_stop_test/yantian_608"
darknet_dir = "/home/sakulaki/yolo-yuli/darknet"
det_segment = 0.05
det_classify = 0.1
save_path = "/home/sakulaki/yolo-yuli/one_stop_test/yantian_jpg"

# cut tif file to 608x608 images. For each tif, it will generate a folder to put 608 images ###########################
print(colorama.Fore.GREEN + "[INFO] cut 608 images from tif file" + colorama.Fore.WHITE)
os.makedirs(output_tif_608s, exist_ok=True)
if len(sys.argv) > 1 and sys.argv[1] == "yeah":
    asap_to_image(input_tif_files, output_tif_608s)

# for each tif, run segmentation and classification, generate jpg/xml for labelme #####################################
tif_names = scan_subdirs(output_tif_608s)
not_run = True
for tif_name in tif_names:
    if tif_name.endswith("_segment") or tif_name.endswith("_classify"):
        continue
    if not_run:
        not_run = False
    else:
        break
    print(colorama.Fore.RED + "[INFO] ########################################" + colorama.Fore.WHITE)
    image_path = os.path.join(output_tif_608s, tif_name)
    
    # get the list of 608 image full pathnames ########################################################################
    images = scan_files(image_path)

    # generate txt file for current tif ###############################################################################
    print(colorama.Fore.GREEN + "[INFO] generate txt for " + tif_name + colorama.Fore.WHITE)
    gen_txt_for_dir(images, output_tif_608s, tif_name)

    # run darknet test ################################################################################################
    darknet_path = darknet_dir
    segment(darknet_path, image_path)
    os.remove(image_path+".txt")

    # evaluate predictions and convert coordinates to xmls ############################################################
    print(colorama.Fore.GREEN + "[INFO] evaluate predictions and write coordinates into xmls" + colorama.Fore.WHITE)
    result_dir = os.path.join(darknet_path, "results")
    classes_list = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
    dict_pic_info = get_predictions_result(result_dir, classes_list)
    img_size = 608
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    det = det_segment
    prediction_convert(dict_pic_info, classes_list, img_size, segment_xml_path, det)

    # copy xmls from segment folder to jpg folder, for purpose of cropping images #####################################
    print(colorama.Fore.GREEN + "[INFO] copy xmls from segment folder to jpg folder" + colorama.Fore.WHITE)
    xmls = scan_files(segment_xml_path, postfix=".xml")
    for xml in xmls:
        shutil.copy(xml, image_path)
    # copy_files(segment_xml_path, image_path, postfix=".xml")

    # crop cells out of 608 jpgs and save into numpy array, based on predicted xmls ###################################
    print(colorama.Fore.GREEN + "[INFO] crop cells out of 608 jpgs and save into numpy array, based on xmls" + colorama.Fore.WHITE)
    classes_dict = {"HSIL":0, "ASCH":0, "LSIL":0, "ASCUS":0, "SCC":0}
    files_list = scan_files(image_path, postfix=".xml")
    img_size = 299
    cell_numpy, cell_numpy_index = get_cells(files_list, classes_dict, img_size)
    print(cell_numpy.shape)
    print(colorama.Fore.BLUE + "segmentation result: {}".format(sorted(classes_dict.items())) + colorama.Fore.WHITE)

    # delete xmls_segment from jpg folder and copy jpgs to segment folder #############################################
    print(colorama.Fore.GREEN + "[INFO] delete xmls_segment from jpg folder and copy jpgs to segment folder" + colorama.Fore.WHITE)
    xmls = scan_files(image_path, postfix=".xml")
    for xml in xmls:
        os.remove(xml)
        jpg = os.path.join(image_path, os.path.basename(os.path.splitext(xml)[0])+".jpg")
        shutil.copy(jpg, segment_xml_path)
    #remove_files(image_path, postfix=".xml")
    
    # run classification ##############################################################################################
    print(colorama.Fore.GREEN + "[INFO] run classification" + colorama.Fore.WHITE)   
    model = xception_init("Xception_finetune.h5")
    predictions = xception_predict(cell_numpy, batch_size=20, model=model)
    print(predictions.shape)
    # del cell_numpy

    # generate new dict_pic_info mapping ##############################################################################
    print(colorama.Fore.GREEN + "[INFO] generate new dict_pic_info mapping" + colorama.Fore.WHITE)
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
    print(colorama.Fore.BLUE + "segment_in_classify: {}".format(sorted(segment_in_classify.items())) + colorama.Fore.WHITE)

    # generate xmls, based on classification results ##################################################################
    print(colorama.Fore.GREEN + "[INFO] generate xmls based on classification" + colorama.Fore.WHITE)
    img_size = 608
    classify_xml_path = os.path.join(output_tif_608s, tif_name+"_classify")
    det = det_classify
    xception_convert(dict_pic_info_all, classes_all, img_size, classify_xml_path, det)

    # copy jpgs from jpg folder to xmls_classify folder ###############################################################
    print(colorama.Fore.GREEN + "[INFO] copy jpgs from jpg folder to xmls_classify folder" + colorama.Fore.WHITE)
    xmls = scan_files(classify_xml_path, postfix=".xml")
    for xml in xmls:
        jpg = os.path.join(image_path, os.path.basename(os.path.splitext(xml)[0])+".jpg")
        shutil.copy(jpg, classify_xml_path)

    # write auto_labeling info into csv ###############################################################################
    print(colorama.Fore.GREEN + "[INFO] write auto_labeling info into csv" + colorama.Fore.WHITE)
    csv_file = os.path.join(output_tif_608s, tif_name+".csv")
    dict_to_csv(dict_pic_info_all, classes_list, classes_all, csv_file)

    # generate confusion matrix #######################################################################################
    print(colorama.Fore.GREEN + "[INFO] generate confusion matrix" + colorama.Fore.WHITE)
    matrix = confusion_matrix(classes_all, cell_numpy_index, predictions)
    xlsx = os.path.join(output_tif_608s, tif_name+".xlsx")
    generate_xlsx(classes_all, matrix, xlsx)

    # generate asap_xml from labelimg_xmls
    print(colorama.Fore.GREEN + "[INFO] generate asap xml from labelimg xmls" + colorama.Fore.WHITE)
    xml_asap_segment = os.path.join(output_tif_608s, tif_name+"_segment.xml")
    gen_asap_xml(xml_asap_segment, segment_xml_path)
    xml_asap_classify = os.path.join(output_tif_608s, tif_name+"_classify.xml")
    gen_asap_xml(xml_asap_classify, classify_xml_path)

    # move current directories upwards ################################################################################
    print(colorama.Fore.GREEN + "[INFO] move current directories upwards" + colorama.Fore.WHITE)
    os.makedirs(save_path, exist_ok=True)
    os.system("mv {} {}".format(image_path, save_path))
    os.system("mv {} {}".format(segment_xml_path, save_path))
    os.system("mv {} {}".format(classify_xml_path, save_path))
    os.system("mv {} {}".format(csv_file, save_path))
    os.system("mv {} {}".format(xlsx, save_path))
    os.system("mv {} {}".format(xml_asap_segment, save_path))
    os.system("mv {} {}".format(xml_asap_classify, save_path))
