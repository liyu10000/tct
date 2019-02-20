#!/usr/bin/env sh
/home/mpc/caffe/build/tools/caffe train --solver=/home/mpc/train/lingxin/res18/solver.prototxt -weights /home/mpc/train/lingxin/res18/model/tmp_model/model_4gpui_40w2_iter_2000.caffemodel --gpu 0,1,2,3 2>&1 | tee /home/mpc/train/lingxin/res18/log/23.txt
