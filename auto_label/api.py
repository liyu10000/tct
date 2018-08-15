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
from Xception_convert import xception_convert, xception_to_csv
from Inception_classify import inception_init, inception_predict
from Inception_convert import inception_convert, inception_to_csv
from confusion_matrix import confusion_matrix, generate_xlsx
from xml_to_asap import gen_asap_xml
from extract_feature import extract_feature
from xgboost_predict import xgboost_predict
from utils import scan_files, scan_subdirs, get_unrunned_tif, dict_to_csv, csv_to_dict, write_line_to_csv

colorama.init()

# configuration ###################################################################################################
input_tif_files = "/media/DATA/2018-06-12-normal"
output_tif_608s = "/media/DATA/2018-06-12-normal_608"
darknet_path = "/home/tsimage/Documents/darknet"
det_segment = 0.05
det_classify = 0.1
save_path = "/media/DATA/2018-06-12-normal_jpg"
diagnosis = "NORMAL"
###################################################################################################################

classes_darknet = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
classes_xception = ["ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", 
               "MC", "RC", "SC", "SCC", "TRI", "VIRUS"]
#classes_inception = ['LSIL', 'EC', 'MC', 'ASCH', 'ADC', 'HSIL', 'AGC1', 'RC', 'VIRUS', 'SC', 'ACTINO', 'SCC', 'FUNGI', 'ASCUS', 'AGC2', 'GEC', 'CC', 'TRI']
classes_inception = ["ASCH", "ASCUS", "HSIL", "LSIL", "NORMAL", "SCC"]

def tif_to_608():
    print(colorama.Fore.GREEN + "[INFO] cut 608 images from tif file" + colorama.Fore.WHITE)
    os.makedirs(output_tif_608s, exist_ok=True)
    os.makedirs(save_path, exist_ok=True)
    tif_name_ext = get_unrunned_tif(input_tif_files, save_path)
    if tif_name_ext == "":
        print(colorama.Fore.RED + "[INFO] data processing finished" + colorama.Fore.WHITE)
        sys.exit(1)
    asap_to_image(os.path.join(input_tif_files, tif_name_ext), output_tif_608s)
    tif_name = os.path.splitext(tif_name_ext)[0]
    return tif_name

def darknet_run(tif_name):
    # get the list of 608 image full pathnames
    image_path = os.path.join(output_tif_608s, tif_name)
    images = scan_files(image_path)
    # generate txt file for current tif
    print(colorama.Fore.GREEN + "[INFO] generate txt for " + tif_name + colorama.Fore.WHITE)
    gen_txt_for_dir(images, output_tif_608s, tif_name)
    # run darknet test
    segment(darknet_path, image_path)

def darknet_analyze():
    # evaluate predictions and convert coordinates to xmls
    print(colorama.Fore.GREEN + "[INFO] evaluate predictions and write coordinates into xmls" + colorama.Fore.WHITE)
    result_dir = os.path.join(darknet_path, "results")
    #classes_darknet = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
    dict_pic_info = get_predictions_result(result_dir, classes_darknet)
    return dict_pic_info

def darknet_write(dict_pic_info, tif_name):
    img_size = 608
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    prediction_convert(dict_pic_info, classes_darknet, img_size, segment_xml_path, det_segment)

def copy_xml_from_seg_to_608(tif_name):
    # copy xmls from segment folder to jpg folder, for purpose of cropping images
    print(colorama.Fore.GREEN + "[INFO] copy xmls from segment folder to jpg folder" + colorama.Fore.WHITE)
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    image_path = os.path.join(output_tif_608s, tif_name)
    xmls = scan_files(segment_xml_path, postfix=".xml")
    for xml in xmls:
        shutil.copy(xml, image_path)

def gen_np_array(image_path, classes_darknet):
    # crop cells out of 608 jpgs and save into numpy array, based on predicted xmls
    print(colorama.Fore.GREEN + "[INFO] crop cells out of 608 jpgs and save into numpy array, based on xmls" + colorama.Fore.WHITE)
    classes_dict = {key:0 for key in classes_darknet}
    #image_path = os.path.join(output_tif_608s, tif_name)
    files_list = scan_files(image_path, postfix=".xml")
    img_size = 299
    cell_numpy, cell_numpy_index = get_cells(files_list, classes_dict, img_size)
    print(cell_numpy.shape)
    print(colorama.Fore.BLUE + "segmentation result: {}".format(sorted(classes_dict.items())) + colorama.Fore.WHITE)
    return cell_numpy, cell_numpy_index

def copy_jpg_from_608_to_seg(tif_name):
    # delete xmls_segment from jpg folder and copy jpgs to segment folder
    print(colorama.Fore.GREEN + "[INFO] delete xmls_segment from jpg folder and copy jpgs to segment folder" + colorama.Fore.WHITE)
    image_path = os.path.join(output_tif_608s, tif_name)
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    xmls = scan_files(image_path, postfix=".xml")
    for xml in xmls:
        os.remove(xml)
        jpg = os.path.join(image_path, os.path.basename(os.path.splitext(xml)[0])+".jpg")
        shutil.copy(jpg, segment_xml_path)

def xception_run(cell_numpy):
    # run classification
    print(colorama.Fore.GREEN + "[INFO] run classification" + colorama.Fore.WHITE)   
    model = xception_init()
    predictions = xception_predict(cell_numpy, batch_size=20, model=model)
    print(predictions.shape)
    return predictions

def xception_analyze(dict_pic_info, cell_numpy_index, predictions, classes_xception):
    # generate new dict_pic_info mapping
    print(colorama.Fore.GREEN + "[INFO] generate new dict_pic_info mapping" + colorama.Fore.WHITE)
    # classes_xception = ["ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", 
    #                "MC", "RC", "SC", "SCC", "TRI", "VIRUS"]
    # segment_in_classify: {class_i:[segment, classify]}
    segment_in_classify = {key:[0,0] for key in classes_xception}
    index = 0
    dict_pic_info_all = {}
    for prediction in predictions:
        i = np.argmax(prediction)
        class_i = classes_xception[i]
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
    return dict_pic_info_all

def xception_write(tif_name, output_tif_608s, dict_pic_info_all, classes_xception, det_classify):
    # generate xmls, based on classification results
    print(colorama.Fore.GREEN + "[INFO] generate xmls based on classification" + colorama.Fore.WHITE)
    img_size = 608
    classify_xml_path = os.path.join(output_tif_608s, tif_name+"_classify")
    xception_convert(dict_pic_info_all, classes_xception, img_size, classify_xml_path, det_classify)

def inception_run(cell_numpy):
    # run classification
    print(colorama.Fore.GREEN + "[INFO] run classification" + colorama.Fore.WHITE)   
    model = inception_init()
    predictions = inception_predict(cell_numpy, batch_size=20, model=model)
    print(predictions.shape)
    return predictions

inception_analyze = xception_analyze

inception_write = xception_write

def copy_jpg_from_608_to_cla(tif_name):
    # copy jpgs from jpg folder to xmls_classify folder
    print(colorama.Fore.GREEN + "[INFO] copy jpgs from jpg folder to xmls_classify folder" + colorama.Fore.WHITE)
    classify_xml_path = os.path.join(output_tif_608s, tif_name+"_classify")
    image_path = os.path.join(output_tif_608s, tif_name)
    xmls = scan_files(classify_xml_path, postfix=".xml")
    for xml in xmls:
        jpg = os.path.join(image_path, os.path.basename(os.path.splitext(xml)[0])+".jpg")
        shutil.copy(jpg, classify_xml_path)

def write_dict_pic_info(tif_name, dict_pic_info, dict_pic_info_all):
    # write auto_labeling info into csv
    print(colorama.Fore.GREEN + "[INFO] write auto_labeling info into csv" + colorama.Fore.WHITE)
    csv_file_s = os.path.join(output_tif_608s, tif_name+"_s.csv")
    dict_to_csv(dict_pic_info, csv_file_s)
    csv_file_c = os.path.join(output_tif_608s, tif_name+"_c.csv")
    xception_to_csv(dict_pic_info_all, classes_darknet, classes_xception, csv_file_c)

def write_confusion_matrix(tif_name, cell_numpy_index, predictions):
    # generate confusion matrix
    print(colorama.Fore.GREEN + "[INFO] generate confusion matrix" + colorama.Fore.WHITE)
    matrix = confusion_matrix(classes_xception, cell_numpy_index, predictions)
    xlsx = os.path.join(output_tif_608s, tif_name+".xlsx")
    generate_xlsx(classes_xception, matrix, xlsx)

def write_xmls(tif_name):
    # generate asap_xml from labelimg_xmls
    print(colorama.Fore.GREEN + "[INFO] generate asap xml from labelimg xmls" + colorama.Fore.WHITE)
    xml_asap_segment = os.path.join(output_tif_608s, tif_name+"_segment.xml")
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    gen_asap_xml(xml_asap_segment, segment_xml_path)
    classify_xml_path = os.path.join(output_tif_608s, tif_name+"_classify")
    xml_asap_classify = os.path.join(output_tif_608s, tif_name+"_classify.xml")
    gen_asap_xml(xml_asap_classify, classify_xml_path)

def move_folders(tif_name):
    # move current directories to save path
    print(colorama.Fore.GREEN + "[INFO] move current directories to save path" + colorama.Fore.WHITE)
    save_path_i = os.path.join(save_path, tif_name)
    os.makedirs(save_path_i, exist_ok=True)
    related_folders = os.listdir(output_tif_608s)
    for f in related_folders:
        if f.startswith(tif_name):
            os.system("mv {} {}".format(os.path.join(output_tif_608s, f), save_path_i))


if __name__ == "__main__":

    # # run second stage inception program
    # tif_names = os.listdir(save_path)
    # for tif_name in tif_names:
    #     print(colorama.Fore.RED + "[INFO] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" + colorama.Fore.WHITE)
    #     tif_dir = os.path.join(save_path, tif_name)
    #     csv_file_s = os.path.join(tif_dir, tif_name+"_s.csv")
    #     dict_pic_info = csv_to_dict(csv_file_s)
    #     cell_numpy, cell_numpy_index = gen_np_array(os.path.join(tif_dir, tif_name+"_segment"), classes_darknet)
    #     predictions = inception_run(cell_numpy)
    #     dict_pic_info_all = inception_analyze(dict_pic_info, cell_numpy_index, predictions, classes_inception)
    #     inception_write(tif_name, tif_dir, dict_pic_info_all, classes_inception, det_classify)
    #     csv_file_c2 = os.path.join(tif_dir, tif_name+"_c2.csv")
    #     inception_to_csv(dict_pic_info_all, classes_darknet, classes_inception, csv_file_c2)
    #     csv_file_f = extract_feature(csv_file_c2, diagnosis=diagnosis)
    #     pred_class_i = xgboost_predict(csv_file_f)
    #     print("{}: {}".format(tif_name, pred_class_i))

    # # run second stage Xception program
    # tif_names = os.listdir(save_path)
    # for tif_name in tif_names:
    #     tif_dir = os.path.join(save_path, tif_name)
    #     csv_file_s = os.path.join(tif_dir, tif_name+"_s.csv")
    #     dict_pic_info = csv_to_dict(csv_file_s)
    #     cell_numpy, cell_numpy_index = gen_np_array(os.path.join(tif_dir, tif_name+"_segment"), classes_darknet)
    #     predictions = xception_run(cell_numpy)
    #     dict_pic_info_all = xception_analyze(dict_pic_info, cell_numpy_index, predictions, classes_xception)
    #     xception_write(tif_name, tif_dir, dict_pic_info_all, classes_xception, det_classify)
    #     csv_file_c2 = os.path.join(tif_dir, tif_name+"_c2.csv")
    #     xception_to_csv(dict_pic_info_all, classes_darknet, classes_xception, csv_file_c2)
    #     csv_file_f = extract_feature(csv_file_c2, diagnosis=diagnosis)
    #     xgboost_predict(csv_file_f)


    # # run a complete test [Xception]
    # print(colorama.Fore.RED + "[INFO] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" + colorama.Fore.WHITE)
    # tif_name = tif_to_608()
    # darknet_run(tif_name)
    # dict_pic_info = darknet_analyze()
    # darknet_write(dict_pic_info, tif_name)
    # copy_xml_from_seg_to_608(tif_name)
    # cell_numpy, cell_numpy_index = gen_np_array(os.path.join(output_tif_608s, tif_name), classes_darknet)
    # copy_jpg_from_608_to_seg(tif_name)
    # predictions = xception_run(cell_numpy)
    # dict_pic_info_all = xception_analyze(dict_pic_info, cell_numpy_index, predictions, classes_xception)
    # xception_write(tif_name, output_tif_608s, dict_pic_info_all, classes_xception, det_classify)
    # copy_jpg_from_608_to_cla(tif_name)
    # write_dict_pic_info(tif_name, dict_pic_info, dict_pic_info_all)
    # # write_confusion_matrix(tif_name, cell_numpy_index, predictions)
    # # write_xmls(tif_name)
    # move_folders(tif_name)
    # tif_dir = os.path.join(save_path, tif_name)
    # csv_file_c = os.path.join(tif_dir, tif_name+"_c.csv")
    # csv_file_f = extract_feature(csv_file_c, diagnosis=diagnosis)
    # pred_class_i = xgboost_predict(csv_file_f)
    # print("{}: {}".format(tif_name, pred_class_i))
    # result_csv = os.path.join(save_path, "result.csv")
    # write_line_to_csv(result_csv, [tif_name, pred_class_i])


    # run a complete test [inception]
    print(colorama.Fore.RED + "[INFO] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" + colorama.Fore.WHITE)
    tif_name = tif_to_608()
    darknet_run(tif_name)
    dict_pic_info = darknet_analyze()
    darknet_write(dict_pic_info, tif_name)
    copy_xml_from_seg_to_608(tif_name)
    cell_numpy, cell_numpy_index = gen_np_array(os.path.join(output_tif_608s, tif_name), classes_darknet)
    copy_jpg_from_608_to_seg(tif_name)
    predictions = inception_run(cell_numpy)
    dict_pic_info_all = inception_analyze(dict_pic_info, cell_numpy_index, predictions, classes_xception)
    inception_write(tif_name, output_tif_608s, dict_pic_info_all, classes_xception, det_classify)
    copy_jpg_from_608_to_cla(tif_name)
    write_dict_pic_info(tif_name, dict_pic_info, dict_pic_info_all)
    # write_confusion_matrix(tif_name, cell_numpy_index, predictions)
    # write_xmls(tif_name)
    move_folders(tif_name)
    tif_dir = os.path.join(save_path, tif_name)
    csv_file_c = os.path.join(tif_dir, tif_name+"_c.csv")
    csv_file_f = extract_feature(csv_file_c, diagnosis=diagnosis)
    pred_class_i = xgboost_predict(csv_file_f)
    print("{}: {}".format(tif_name, pred_class_i))
    result_csv = os.path.join(save_path, "result.csv")
    write_line_to_csv(result_csv, [tif_name, pred_class_i])