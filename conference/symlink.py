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


def make_symlink(src_dir, dst_dir, postfix, depth=0, makedir=False):
    src_files = scan_files(src_dir, postfix=postfix)

    for src_file in src_files:
        tokens = src_file.rsplit(os.sep, depth+1)
        dst_file = os.path.join(dst_dir, *tokens[1:])
        if makedir:
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        os.symlink(src_file, dst_file)


if __name__ == "__main__":
    src_dir = "/home/hdd0/Develop/xxx/cells/HSIL_B"
    dst_dir = "/home/hdd0/Develop/xxx/cells"
    postfix = ".bmp"
    depth = 0
    makedir = False


    make_symlink(src_dir, dst_dir, postfix, depth, makedir)