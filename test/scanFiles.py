#coding=utf-8  

"""
扫描指定目录下的文件，或者匹配指定后缀和前缀的函数。


如果要扫描指定目录下的文件，包括子目录，调用scan_files("/export/home/test/")

如果要扫描指定目录下的特定后缀的文件（比如jar包），包括子目录，调用scan_files("/export/home/test/", postfix=".jar")

如果要扫描指定目录下的特定前缀的文件（比如test_xxx.py），包括子目录，调用scan_files("/export/home/test/", prefix="test_")
"""

import os  
  
def scan_files(directory,prefix=None,postfix=None):  
    files_list=[]  
      
    for root, sub_dirs, files in os.walk(directory):  
        for special_file in files:  
            if postfix:  
                if special_file.endswith(postfix):  
                    files_list.append(os.path.join(root,special_file))  
            elif prefix:  
                if special_file.startswith(prefix):  
                    files_list.append(os.path.join(root,special_file))  
            else:  
                files_list.append(os.path.join(root,special_file))  
                            
    return files_list  


print(scan_files("E:/liyu/files"))