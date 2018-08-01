import os
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

# path = os.getcwd()
path = "E:/data-yantian"
filenames = scan_files(path, postfix=".kfb")
print("total of " + str(len(filenames)) + " filenames found")

# use with caution: it doesn't work with the case that folder name has blank spaces
for filename in filenames:
    # replace blank spaces with "_"
    if " " in filename:
        os.rename(filename, filename.replace(" ", "-"))
        print(filename + " has blank space")
    # try:
        # os.rename(filename, filename.replace(" ", "-"))
    # except:
        # os.remove(filename.replace(" ", "-"))
        # os.rename(filename, filename.replace(" ", "-"))
        
    # if len(os.path.basename(filename)) > 19:
        # print(os.path.join(filename.rsplit("\\",1)[0], filename[-23:]))
        # os.rename(filename, os.path.join(filename.rsplit("\\",1)[0], filename[-23:]))

    # # change file extension
    # name, ext = os.path.splitext(filename)
    # os.rename(filename, name + ".jpg")

    # # modify endings like xxxxxxxx_Annotation-34, replace "_" with " "
    # name, ext = os.path.splitext(filename)
    # newname = ""
    # if name[-4:].isdigit():  # 4 digits
    #     newname = name[:-5] + " " + name[-4:]
    # elif name[-3:].isdigit():  # 3 digits
    #     newname = name[:-4] + " " + name[-3:]
    # elif name[-2:].isdigit():  # 2 digits
    #     newname = name[:-3] + " " + name[-2:]
    # elif name[-1:].isdigit():  # 1 digit
    #     newname = name[:-2] + " " + name[-1:]
    # os.rename(filename, newname+ext)
