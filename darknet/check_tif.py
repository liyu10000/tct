import os

def scan_files(directory, prefix=None, postfix=None):
    files_list = set()

    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.add(special_file[:19])
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.add(special_file[:19])
            else:
                files_list.add(special_file[:19])

    return files_list
    
files_in_train = scan_files(os.path.join(os.getcwd(), "train"), postfix=".jpg")
files_in_test = scan_files(os.path.join(os.getcwd(),  "test"), postfix=".jpg")
print(files_in_train & files_in_test)
