## data precessing
 - cellSampling.py
 - cell_to_asap.py
 - cellSamplingFixedSize6.py

### cellSampling.py 
 - **cut cells from kfb/tif wsis to cell jpgs, for purpose of checking**
 - this script will cut twice the size of labeled box, and name saved jpg with filename_x_y_w_h.jpg
 - how to use:
     1. open cellSampling.py and slide to the end, there are two variables to change at every run
     2. path_in: full/path/to/path_in, is the path where kfb/tif files reside, the tree view of path_in should be like this:
             path_in:
                 sub_dir1:
                     xxxx.kfb
                     xxxx.xml
                 sub_dir2:
                     yyyy.kfb
                     yyyy.xml
                 ....
     3. path_out is the path where jpgs will save into, the result tree view of path_out will be like this:
             path_out:
                 sub_dir1:
                     xxxx:
                         ASCUS:
                             xxxx_x_y_w_h.jpg
                         LSIL:
                             xxxx_x_y_w_h.jpg
                 sub_dir2:
                     yyyy:
                         ASCUS:
                             yyyy_x_y_w_h.jpg
                         MC:
                             yyyy_x_y_w_h.jpg
                 ....

### cell_to_asap.py
 - **collect checked jpgs/labels information and write back to asap xml**
 - how to use:
     1. open cell_to_asap.py and slide to the end, there are two variables to change at every run
     2. path_in: should be the same to the path_out in cellSampling.py, the tree view of path_in should be like this (xxxx and yyyy represents kfb/tif filename):
             path_in:
                 sub_dir1:
                     xxxx:
                         ASCUS:
                             xxxx_x_y_w_h.jpg
                         LSIL:
                             xxxx_x_y_w_h.jpg
                 sub_dir2:
                     yyyy:
                         ASCUS:
                             yyyy_x_y_w_h.jpg
                         MC:
                             yyyy_x_y_w_h.jpg
                 ....
     3. path_out: should be the same to the path_in in cellSampling.py. **note**: remember to make a copy of old xmls before writing new xmls.
             path_out:
                 sub_dir1:
                     xxxx.xml
                 sub_dir2:
                     yyyy.xml
                 ....
                 
### cellSamplingFixedSize6.py
 - **cut from kfb/tif wsis to fixed sized jpg images for training**
 - info: the working function "cut_cells" will cut images at given size and place label box at given position. *note*: the position parameter can be randomized so that the image will have a randomly placed label box inside.
 - how to use:
     1. open cellSamplingFixedSize6.py and slide to the end, there are two variables to change at every run
     2. path_in: the file path that contains kfb/tif wsis and corresponding xmls, no special folder tree structure needed.
     3. path_out: the output jpgs
             path_out:
                 xxxx:
                     ASCUS:
                         xxxx_x_y_px_py.jpg
                     MC:
                         xxxx_x_y_px_py.jpg
                 yyyy:
                     MC:
                         yyyy_x_y_px_py.jpg
                     HSIL:
                         yyyy_x_y_px_py.jpg
                 ....