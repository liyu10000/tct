import os
import openslide
import scipy.misc
from tslide.tslide import TSlide

classes = ['VIRUS', 'CC', 'HSIL', 'FUNGI', 'AGC1', 'AGC3', 
           'EC', 'LSIL', 'ASCH', 'AGC2', 'ACTINO', 'ASCUS', 'SCC', 'ADC', 'TRI',
           'MC', 'SC', 'RC', 'GEC', 'NORMAL']

def get_position(src_txt_dir, des_tif_dir):
    """
        src_txt_dir: the folder that contains subfolders that contain txt file with label coordinates
        des_tif_dir: the folder that contains target tifs
        return: positions: {tif: [(class_i, x, y, w, h),]}
    """
    def tif_match(src_tif, des_tif):
        return src_tif[:19] == des_tif[:19]
    def tif_in(src_tif, des_tifs):
        for des_tif in des_tifs:
            if tif_match(src_tif, des_tif):
                return True
        return False
        
    src_tifs = os.listdir(src_txt_dir)
    des_tifs = os.listdir(des_tif_dir)
    positions = {}
    for src_tif in src_tifs:
        if (not src_tif.startswith("2017")) or (not tif_in(src_tif, des_tifs)):
            continue
        positions[src_tif] = []
        src_tif_txts = os.listdir(os.path.join(src_txt_dir, src_tif))
        for scr_tif_txt in src_tif_txts:
            with open(os.path.join(src_txt_dir, src_tif+'/'+scr_tif_txt), 'r') as f:
                for line in f:
                    tokens = line.strip().split(',')
                    class_i = tokens[4]
                    if not class_i in classes:
                        continue
                    x = int(tokens[-2]) + int(tokens[0])
                    y = int(tokens[-1]) + int(tokens[1])
                    w = int(tokens[2])
                    h = int(tokens[3])
                    positions[src_tif].append((class_i,x,y,w,h))
    return positions

def cut_fixed_size(tif_dir, positions, size, save_path):
    """
        tif_dir: tif folder
        positions: {tif: [(class_i, x, y, w, h),]}
        size: target jpg size
        save_path: target save path
    """
    def get_x_y(box, size):
        x_center = box[1] + box[3]/2.0
        y_center = box[2] + box[4]/2.0
        x = int(x_center - size/2.0)
        y = int(y_center - size/2.0)
        return (x, y)

    for tif,boxes in positions.items():
        #slide = openslide.OpenSlide(os.path.join(tif_dir, tif+".tif"))
        try:
            slide = openslide.OpenSlide(os.path.join(tif_dir, tif+".tif"))
        except:
            slide = TSlide(os.path.join(tif_dir, tif+".kfb"))
        for box in boxes:
            save_path_i = os.path.join(save_path, box[0])
            os.makedirs(save_path_i, exist_ok=True)
            x, y = get_x_y(box, size)
            cell = slide.read_region((x, y), 0, (size, size)).convert("RGB")
            scipy.misc.imsave(os.path.join(save_path_i, "{}_{}_{}.jpg".format(tif, x, y)), cell)
        slide.close()
        print("processed: {}".format(tif))

def cut_same_size(tif_dir, positions, save_path):
    """
        tif_dir: tif folder
        positions: {tif: [(class_i, x, y, w, h),]}
        save_path: target save path, image naming: tif_x_y_w_h.jpg
    """
    for tif,boxes in positions.items():
        #slide = openslide.OpenSlide(os.path.join(tif_dir, tif+".tif"))
        try:
            slide = openslide.OpenSlide(os.path.join(tif_dir, tif+".tif"))
        except:
            slide = TSlide(os.path.join(tif_dir, tif+".kfb"))
        for box in boxes:
            save_path_i = os.path.join(save_path, box[0])
            os.makedirs(save_path_i, exist_ok=True)
            x, y = box[1], box[2]
            w, h = box[3], box[4]
            cell = slide.read_region((x, y), 0, (w, h)).convert("RGB")
            cell.save(os.path.join(save_path_i, "{}_x{}_y{}_w{}_h{}.jpg".format(tif, x, y, w, h)))
        slide.close()
        print("processed: {}".format(tif))


if __name__ == "__main__":
    src_txt_dir = "/home/sakulaki/yolo-yuli/xxx/data_unchecked_20180818/batch0"
    des_tif_dir = "/home/sakulaki/yolo-yuli/last_step/LSIL" 
    positions = get_position(src_txt_dir, des_tif_dir)

    # # cut a fixed sized image around the label box
    # size = 2048
    # save_path = "/home/sakulaki/yolo-yuli/xxx/online_2048_center_part2"
    # cut_fixed_size(des_tif_dir, positions, size, save_path)

    # cut out the label box, as it is
    save_path = "/home/sakulaki/yolo-yuli/xxx/online_samesize_0825_part1"
    cut_same_size(des_tif_dir, positions, save_path)