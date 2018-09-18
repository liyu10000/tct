import os
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

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

datagen = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    # rescale=0.5,
    fill_mode="reflect"
)

def aug_single(image, image_out_path, n):
    img = load_img(image)
    img_array = img_to_array(img)
    img_array = img_array.reshape((1,) + img_array.shape)

    i = 0
    for batch in datagen.flow(img_array, batch_size=1, save_to_dir=image_out_path,
                              save_prefix="20180514", save_format="jpg"):
        i += 1
        if i > n:
            break

# def aug_multiple(image_in_path, image_out_path, n):
#     i = 0
#     for batch in datagen.flow_from_directory(directory=image_in_path, target_size=(224, 224),
#                                              save_to_dir=image_out_path,
#                                              save_prefix="20180514", save_format="jpg"):
#         i += 1
#         if i > n:
#             break


if __name__ == "__main__":
    # image = "../res/cats_n_dogs/cat.jpg"
    # image_out_path = "../res/cats_n_dogs/preview"
    # n = 20
    # aug_single(image, image_out_path, n)

    image_in_path = "C:\\liyu\\files\\tiff\\cells"
    image_out_path = "C:\\liyu\\files\\tiff\\cells\\output"
    n = 100
    images = scan_files(image_in_path, postfix=".jpg")
    print("# images: " + str(len(images)))
    for image in images:
        aug_single(image, image_out_path, int(n/len(images)))
    print("# images generated: " + str(int(n/len(images))*len(images)))


