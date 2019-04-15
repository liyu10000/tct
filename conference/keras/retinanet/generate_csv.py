import os
import csv


classes = ["AGC", "HSIL-SCC_G", "SCC_R", "EC", "ASCUS", "LSIL", "CC", "VIRUS", "FUNGI", "ACTINO", "TRI", "PH", "SC"]


def read_labels(txt_name, size=608):
    labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            class_name = classes[int(tokens[0])]
            cx, cy = float(tokens[1])*size, float(tokens[2])*size
            w, h = float(tokens[3])*size, float(tokens[4])*size
            x1, y1 = int(cx - w / 2), int(cy - h / 2)
            x2, y2 = int(cx + w / 2), int(cy + h / 2)
            labels.append([x1, y1, x2, y2, class_name])
    return labels


def generate_anno_csv(img_list_file, csv_name):
    # read and collect img list
    names = []
    with open(img_list_file, 'r') as f:
        for line in f.readlines():
            img_name = line.strip()
            txt_name = os.path.splitext(img_name)[0] + '.txt'
            names.append((img_name, txt_name))
    print("# of images:", len(names))
            
    # write csv
    with open(csv_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for i,name in enumerate(names):
            img_name, txt_name = name
            labels = read_labels(txt_name)
            for label in labels:
                writer.writerow([img_name] + label)
            if i % 50000 == 0:
                print("# of processed images:", i)
    print("finished writing annotation csv")

    
def generate_clas_csv(csv_name):
    with open(csv_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for i,class_i in enumerate(classes):
            writer.writerow([class_i, i])
    print("finished writing name mapping csv")
    
                
if __name__ == "__main__":
    img_list_file = "/home/ssd_array0/Data/batch6.4_1216/train-gnet2.txt"
    anno_csv_name = "/home/ssd_array0/Data/batch6.4_1216/train-gnet3.csv"
    generate_anno_csv(img_list_file, anno_csv_name)
    
    clas_csv_name = "/home/ssd_array0/Data/batch6.4_1216/names-gnet3.csv"
    generate_clas_csv(clas_csv_name)