import os
from cell_slicing_tif import cut_cells
from rotate import do_rotate
from select_separate import split_test_from_train, split_valid_from_train
from generate_txt import gen_txt


def process(path_in, path_out):
    """prepare training data for darknet
    :params path_in: the directory storing kfb/tif, the tree view of path_in should be:
                     path_in:
                        sub_dir1:
                            xxxx.kfb
    :params path_out: resulting training data should include three folders: train/valid/test, and three corresponding txts
    """

    # make train folder to store all intermediate data
    path_train = os.path.join(path_out, "train")
    
    # cut from kfb/tif to 608 sized jpgs/xmls
    cut_cells(path_in, path_train, size=608)

    # do augmentation: rotate
    do_rotate(path_train)

    # select from train folder to valid/test folder
    split_test_from_train(path_train, factor=0.1)
    split_valid_from_train(path_train, factor=0.1)

    # generate txt files
    gen_txt(path_out)


if __name__ == "__main__":
    path_in = ""
    path_out = ""
    process(path_in, path_out)