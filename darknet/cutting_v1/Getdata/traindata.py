# -*- coding: utf-8 -*-
import os;
import shutil;

def rename_by_count(path): #按序号命名
    count = 1000;
    filelist = os.listdir(path)  # 该文件夹下所有的文件（包括文件夹）
    for files in filelist:  # 遍历所有文件
        Olddir = os.path.join(path, files);  # 原来的文件路径
        if os.path.isdir(Olddir):  # 如果是文件夹则跳过
            continue;
        filename = os.path.splitext(files)[0];  # 文件名
        filetype = os.path.splitext(files)[1];  # 文件扩展名
        Newdir = os.path.join(path, str(count) + filetype);  # 新的文件路径
        os.rename(Olddir, Newdir);  # 重命名
        count += 1;


def listname(path,idtxtpath):
    filelist = os.listdir(path);  # 该文件夹下所有的文件（包括文件夹）
    f = open(idtxtpath, 'w');
    for files in filelist:  # 遍历所有文件
        Olddir = os.path.join(path, files);  # 原来的文件路径
        if os.path.isdir(Olddir):  # 如果是文件夹则跳过
            continue;
        filename = os.path.splitext(files)[0];  # 文件名
        filetype = os.path.splitext(files)[1];  # 文件扩展名
        #Newdir = os.path.join(path, "1000" + filetype);  # 新的文件路径: path+filename+type
        f.write(filename);
        f.write('\n');
    f.close();


def imgid_list(imgpath, savepath, num):
    #rename_by_count(imgpath);

    path1 = savepath + "/validateImage";
    path2 = savepath + "/trainImage";
    if not os.path.exists(path1):
        os.mkdir(path1);
    if not os.path.exists(path2):
        os.mkdir(path2);
    xmlpath1 = savepath + "/validateImageXML";
    xmlpath2 = savepath + "/trainImageXML";
    if not os.path.exists(xmlpath1):
        os.mkdir(xmlpath1);
    if not os.path.exists(xmlpath2):
        os.mkdir(xmlpath2);

    filelist = os.listdir(imgpath);
    count = 0;
    for files in filelist:
        olddir = os.path.join(imgpath, files);
        newdir1 = os.path.join(path1, files);
        newdir2 = os.path.join(path2, files);
        filename = os.path.splitext(files)[0];  # 文件名
        xmldir = savepath + "/xml";
        xmldir1 = savepath + "/validateImageXML";
        xmldir2 = savepath + "/trainImageXML";
        if count < num:
            shutil.copy(olddir, newdir1); #validate
            xmlolddir = os.path.join(xmldir, filename + ".xml");
            xmlnewdir = os.path.join(xmldir1,filename + ".xml");
            shutil.copy(xmlolddir,xmlnewdir);
            shutil.copy(xmlolddir, newdir1);
        else:
            shutil.copy(olddir, newdir2);
            xmlolddir = os.path.join(xmldir, filename + ".xml");
            xmlnewdir = os.path.join(xmldir2, filename + ".xml");
            shutil.copy(xmlolddir, xmlnewdir);
            shutil.copy(xmlolddir, newdir2);
        count=count+1;

    imgidtxtpath1 = savepath + "/validateImageId.txt";
    imgidtxtpath2 = savepath + "/trainImageId.txt";
    listname(path1, imgidtxtpath1);
    listname(path2, imgidtxtpath2);





#rename_by_count;   # 给图片按序号给名字
savepath = os.getcwd()
imgpath = savepath+"/Image"
val_num=16   #验证集数量，可修改
imgid_list(imgpath,savepath,val_num);