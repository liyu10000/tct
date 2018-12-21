import os
import openslide
from xml.dom.minidom import parse
import xml.dom.minidom
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from tslide.tslide import TSlide



# # all 11 classes
# classes = {"#aa0000": "HSIL",
#           "#005500": "LSIL", "#00557f": "ASCUS", "#0055ff": "SCC",
#           "#aa55ff": "EC", "#ff5500": "AGC", "#00aa00": "FUNGI",
#           "#00aa7f": "TRI", "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS"}

# one class
classes = {"#F4FA58":"TRI-deep-l"}


def scan_files(directory, prefix=None, postfix=None):
    files_list = []
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))
    return files_list


def cut_cells(xml_file, save_path):
    # from .xml filename, get .tif/.kfb filename
    filename = os.path.splitext(xml_file)[0]
    try:
        slide = openslide.OpenSlide(filename + ".tif")
    except:
        slide = TSlide(filename + ".kfb")

    basename = os.path.basename(filename)

    # open .xml file
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")
    for annotation in annotations:
        coordinates = annotation.getElementsByTagName("Coordinate")
        # read (x, y) coordinates
        x_coords = [float(coordinate.getAttribute("X")) for coordinate in coordinates]
        y_coords = [float(coordinate.getAttribute("Y")) for coordinate in coordinates]
        
        # get mininum-area-bounding-rectangle
        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)
        
        # 2 times the size of marked region
        x = int(1.5 * x_min - 0.5 * x_max)
        y = int(1.5 * y_min - 0.5 * y_max)
        x_size = int(2 * (x_max - x_min))
        y_size = int(2 * (y_max - y_min))
        
        # # take out the size as it is
        # x = int(x_min)
        # y = int(y_min)
        # x_size = int(x_max - x_min)
        # y_size = int(y_max - y_min)

        # if annotation.getAttribute("Color") in classes:
        # cell_path = os.path.join(save_path, basename)
        # os.makedirs(cell_path, exist_ok=True)
        cell_path = save_path
        cell_name = "{}_x{}_y{}_w{}_h{}.bmp".format(basename, 
                                                    int(x_min), 
                                                    int(y_min), 
                                                    int(x_max-x_min),
                                                    int(y_max-y_min))
        cell_path_name = os.path.join(cell_path, cell_name)
        cell = slide.read_region((x, y), 0, (x_size, y_size)).convert("RGB")
        cell.save(cell_path_name)

        # save yolo-txt
        txt_path_name = os.path.splitext(cell_path_name)[0] + ".txt"
        with open(txt_path_name, 'w') as f:
            f.write("0 0.50 0.50 0.50 0.50\n")

    slide.close()


def main(xml_path, save_path):
    files = scan_files(xml_path, postfix=".xml")
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []

    for xml_file in files:
        tasks.append(executor.submit(cut_cells, xml_file, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))


if __name__ == "__main__":
    xml_path = ""
    save_path = ""

    main(xml_path, save_path)