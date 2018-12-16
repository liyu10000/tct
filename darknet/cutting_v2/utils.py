import shutil
import os


def cp_originfile_from_remote(xml_file, dst_dir):
	shutil.copy(xml_file, dst_dir + "/" + xml_file.split('/')[-1])

	filename = os.path.splitext(xml_file)[0]
	if (os.path.isfile(filename + ".tif")):
		filename = filename + ".tif"
	if (os.path.isfile(filename + ".kfb")):
		filename = filename + ".kfb"

	shutil.copy(filename, dst_dir + "/" + filename.split('/')[-1])

	return (dst_dir + "/" + xml_file.split('/')[-1])


def rm_tempfile_from_local(local_xml_file, path_temp):

	filename = os.path.splitext(local_xml_file)[0]
	local_pic_file = ''
	if (os.path.isfile(filename + ".tif")):
		local_pic_file = filename + ".tif"	
	if (os.path.isfile(filename + ".kfb")):
		local_pic_file = filename + ".kfb"

	try:
		os.remove(local_pic_file)
	except:
		print("#WARNING# ", "fail to rm ", local_pic_file)
	
	try:
		os.remove(local_xml_file)
	except:
		print("#WARNING# ", "fail to rm ", local_xml_file)


def get_path_postfix(filename):
    """
    获取文件名和文件后缀
    :param filename: 待处理文件路径
    :return: (文件名， 文件后缀) 如：a.txt --> return ('a', '.txt')
    """
    basename = os.path.basename(filename)
    return os.path.splitext(basename)


class FilesScanner(object):
    """
    获取文件列表工具类
    """

    def __init__(self, files_path, postfix=None):
        """

        :param files_path: 待扫描文件路径
        :param postfix: 所需文件后缀，['.tif', '.kfb'], 默认为空，即获取该路径下所有文件
        """
        self.files_path = files_path

        if postfix:
            assert isinstance(postfix, list), 'argument [postfix] should be list'

        files = []
        if os.path.isfile(files_path):
            if postfix:
                _, ctype = get_path_postfix(files_path)
                if ctype in postfix:
                    files.append(files_path)
            else:
                files.append(files_path)

        if os.path.isdir(files_path):
            for root, dirs, filenames in os.walk(files_path):
                for filename in filenames:
                    if postfix:
                        _, ctype = get_path_postfix(filename)
                        if ctype in postfix:
                            files.append(os.path.join(root, filename))
                    else:
                        files.append(os.path.join(root, filename))
        # 替换为绝对路径
        files = [os.path.abspath(item) for item in files]

        self.files = files

    def get_files(self):
        return self.files


def generate_name_path_dict(path, postfix=None, output_file_path=None):
    """
    获取大图文件路径 key: value = 文件名：文件路径
    :param path: 待检索文件路径列表
    :param output_file_path: 将生成字典结果写入本地的文件路径，含文件名称
    :param postfix: 回收文件类型 ['.tif', '.kfb']
    :return: {filename: file_abs_path}
    """

    assert isinstance(path, (str, list)), 'argument [path] should be path or path list'

    files_collection = []

    if isinstance(path, list):
        for item in path:
            files_collection.extend(FilesScanner(item, postfix).get_files())
    else:
        files_collection = FilesScanner(path, postfix).get_files()

    dict_ = {}
    for file in files_collection:
        key, _ = os.path.splitext(os.path.basename(file))
        key = key.replace(" ", "-")

        if key in dict_:
            value = dict_[key]
            if value.endswith('.kfb'):
                pass
            else:
                dict_[key] = file
        else:
            dict_[key] = file

    # # 如果存在输出路径则写入本地文件
    # if output_file_path:
    #     with open(os.path.join(output_file_path), 'w') as f:
    #         for key, path in dict_.items():
    #             f.write('%s\t%s\n' % (key, path))

    return dict_