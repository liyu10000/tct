import os

def gen_txt_for_dir(images, path, dir):
    # generate txt file for 608s
    save_path = os.path.join(path, dir)
    txt_file = open(os.path.join(path, dir+".txt"), "w")
    for image in images:
        txt_file.write(image+"\n")
    txt_file.close()
    return os.path.join(path, dir+".txt")

    
def segment(darknet_path, image_path):
    # for minitest.data
    cfg_data = {
        "classes": 5,
        "train": os.path.join(darknet_path, "train.txt"),
        "valid": image_path + ".txt",
        "names": os.path.join(darknet_path, "data/minitest.names"),
        "backup": os.path.join(darknet_path, "backup")
    }

    # write cfg_data into minitest.data
    with open(os.path.join(darknet_path, "cfg/minitest.data"), "w") as f:
        for key, value in cfg_data.items():
            f.write("%s = %s\n" % (key, value))

    # change working directory
    current_path = os.getcwd()
    os.chdir(darknet_path)
    # run tests
    # val = os.system(os.path.join(darknet_path, "darknet") + " detector valid "
    #                 + os.path.join(darknet_path, "cfg/minitest.data") + " "
    #                 + os.path.join(darknet_path, "cfg/yolov3-minitest-infer.cfg") + " "
    #                 + os.path.join(darknet_path, "backup/yolov3-minitest.backup"))
    # val = os.system("%s detector valid %s %s %s" %
    #                 (os.path.join(darknet_path, "darknet"),
    #                  os.path.join(darknet_path, "cfg/minitest.data"),
    #                  os.path.join(darknet_path, "cfg/yolov3-minitest-infer.cfg"),
    #                  os.path.join(darknet_path, "backup/yolov3-minitest.backup")))
    os.system("./darknet detector valid cfg/minitest.data cfg/yolov3-minitest-infer.cfg backup/yolov3-minitest_70000.weights -gpus 0,1")
    os.chdir(current_path)
    os.remove(image_path+".txt")
