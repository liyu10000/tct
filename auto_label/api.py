#this will be one-stop service: from tif to classified images for inspection
import os
import numpy as np
from utils import scan_files, scan_subdirs, copy_files, remove_files
from asap_to_jpg import asap_to_image
from segment import gen_txt_for_dir, segment
from prediction_evaluate import get_predictions_result
from prediction_convert import prediction_convert
from jpg_to_cell import get_cells
from Xception_classify import xception_init, xception_predict


# cut tif file to 608x608 images. For each tif, it will generate a folder to put 608 images
input_tif_files = "/home/sakulaki/yolo-yuli/one_stop_test/tif"
output_tif_608s = "/home/sakulaki/yolo-yuli/one_stop_test/608"
#asap_to_image(input_tif_files, output_tif_608s)

# for each tif, run segmentation and classification, generate jpg/xml for labelme
tif_names = scan_subdirs(output_tif_608s)
for tif_name in tif_names:
    image_path = os.path.join(output_tif_608s, tif_name)
    
    # get the list of 608 image full pathnames
    images = scan_files(image_path)

    # generate txt file for current tif
    print("[INFO] generate txt for " + tif_name)
    gen_txt_for_dir(images, output_tif_608s, tif_name)

    # run darknet test
    darknet_path = "/home/sakulaki/yolo-yuli/darknet"
    segment(darknet_path, image_path)

    # evaluate predictions and convert coordinates to xmls
    print("[INFO] evaluate predictions and write coordinates into xmls")
    result_dir = os.path.join(darknet_path, "results")
    classes_list = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
    dict_pic_info = get_predictions_result(result_dir, classes_list)
    img_size = 608
    segment_xml_path = os.path.join(output_tif_608s, tif_name+"_segment")
    os.makedirs(segment_xml_path, exist_ok=True)
    det = 0.3
    prediction_convert(dict_pic_info, classes_list, img_size, segment_xml_path, det)

    # copy xmls from segment folder to jpg folder, for purpose of cropping images
    copy_files(segment_xml_path, image_path, postfix=".xml")

    # crop cells out of 608 jpgs and save into numpy array, based on predicted xmls
    print("[INFO] crop cells out of 608 jpgs and save into numpy array, based on xmls")
    classes_dict = {"HSIL":0, "ASCH":0, "LSIL":0, "ASCUS":0, "SCC":0}
    files_list = scan_files(image_path, postfix=".xml")
    size = 299
    cell_numpy, cell_numpy_index = get_cells(files_list, classes_dict, size)
    print(cell_numpy.shape)
    print("segmentation result: ", sorted(classes_dict.items()))
    
    # run classification
    print("[INFO] run classification")   
    model = xception_init("Xception_finetune.h5")
    predictions = xception_predict(cell_numpy, 20, model)
    print(predictions.shape)

    # analysis
    classes_all = ("ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", "MC", "RC", "SC", "SCC", "TRI", "VIRUS")
    # segment_in_classify: {class_i:[segment, classify]}
    segment_in_classify = {"ACTINO":[0,0], "ADC":[0,0], "AGC1":[0,0], "AGC2":[0,0], "ASCH":[0,0], "ASCUS":[0,0], 
                           "CC":[0,0], "EC":[0,0], "FUNGI":[0,0], "GEC":[0,0], "HSIL":[0,0], "LSIL":[0,0], 
                           "MC":[0,0], "RC":[0,0], "SC":[0,0], "SCC":[0,0], "TRI":[0,0], "VIRUS":[0,0]} 
    index = 0
    for prediction in predictions:
        i = np.argmax(prediction)
        segment_in_classify[classes_all[i]][1] += 1
        if cell_numpy_index[index][1] == classes_all[i]:
            segment_in_classify[classes_all[i]][0] += 1
        index += 1
    print("segment_in_classify: ", segment_in_classify)

    # generate xmls, based on classification results
    
