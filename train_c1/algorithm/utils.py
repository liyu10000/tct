import os
import logging
from os.path import join as pjoin
from openslide import OpenSlide
import time
import argparse
import numpy as np
import cv2
from scipy import ndimage
import sys
import json
import tensorflow as tf

def mkdirs(dirs):
    """
    Function to make directories iteratively.

    Args:
        @arg dirs: a list or a string contains the path(s) to create.
    """
    if isinstance(dirs, list):
        for dir_path in dirs:
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
    elif isinstance(dirs, str):
        if not os.path.isdir(dirs):
            os.makedirs(dirs)


def setup_args(args):
    pass


def list_all_subdirs(base_dir):
    """
    Function to return all sub-directories in @arg base_dir.
    """
    return [dI for dI in os.listdir(
        base_dir) if os.path.isdir(pjoin(base_dir, dI))]


def setup_logger(log_dir, prefix, save_log=False):
    """
    Function to setup a logger which can be saved in @arg log_dir with prefix.
    """
    logger = logging.getLogger('lbp')
    logger.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)

    if save_log:
        # create file handler which logs even debug messages
        mkdirs(log_dir)
        fh = logging.FileHandler(pjoin(log_dir, '_'.join(
            [prefix, time.strftime('%Y%m%d-%H%M%S', time.gmtime()) + '.log'])))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def get_session():
    """ Construct a modified tf session.
    """
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)


def open_wsi(tumor_wsi_file):
    """
    Function which opens a WSI file @a tumor_wsi_file and store it into a OpenSlide object.

    Args:
        @a tumor_wsi_file: The filename of the WSI.

    """
    if tumor_wsi_file.endswith("kfb"):
        # try:
        #     tumor_wsi_image = TSlide(tumor_wsi_file)
        # except:
        #     print("File {} has format error.".format(tumor_wsi_file))
        #     tumor_wsi_image = None
        pass
    else:
        try:
            tumor_wsi_image = OpenSlide(tumor_wsi_file)
        except OpenSlideUnsupportedFormatError:
            print("File {} has format error.".format(tumor_wsi_file))
            tumor_wsi_image = None
    return tumor_wsi_image


def save_json(file_name, obj):
    """
    Function to dump a json file with specified format. Expect @obj to be JSON serializable.
    """
    with open(file_name, 'w') as f:
        json.dump(obj, f, sort_keys=True, indent=2, separators=(',', ': '))

def load_json(file_name):
    # load json data
    with open(file_name,'r') as f:
        data = json.load(f)
        return data
        
def count_files(direc, extention):
    return len([name for name in os.listdir(direc) if os.path.isfile(pjoin(direc, name)) and name.endswith(extention)])


def normalize_staining(img):
    """
    Adopted from "Classification of breast cancer histology images using Convolutional Neural Networks",
    Teresa Araújo , Guilherme Aresta, Eduardo Castro, José Rouco, Paulo Aguiar, Catarina Eloy, António Polónia,
    Aurélio Campilho. https://doi.org/10.1371/journal.pone.0177544
    Performs staining normalization.
    # Arguments
        img: Numpy image array.
    # Returns
        Normalized Numpy image array.
    """

    # img = cv2.cvtColor(cv2.resize(cv2.imread(img_path), (299, 299)), cv2.COLOR_BGR2RGB)

    Io = 240
    beta = 0.15
    alpha = 1
    HERef = np.array([[0.5626, 0.2159],
                      [0.7201, 0.8012],
                      [0.4062, 0.5581]])
    maxCRef = np.array([1.9705, 1.0308])

    h, w, c = img.shape
    img = img.reshape(h * w, c)
    OD = -np.log((img.astype("uint16") + 1) / Io)
    ODhat = OD[(OD >= beta).all(axis=1)]
    W, V = np.linalg.eig(np.cov(ODhat, rowvar=False))

    Vec = -V.T[:2][::-1].T  # desnecessario o sinal negativo
    That = np.dot(ODhat, Vec)
    phi = np.arctan2(That[:, 1], That[:, 0])
    minPhi = np.percentile(phi, alpha)
    maxPhi = np.percentile(phi, 100 - alpha)
    vMin = np.dot(Vec, np.array([np.cos(minPhi), np.sin(minPhi)]))
    vMax = np.dot(Vec, np.array([np.cos(maxPhi), np.sin(maxPhi)]))
    if vMin[0] > vMax[0]:
        HE = np.array([vMin, vMax])
    else:
        HE = np.array([vMax, vMin])

    HE = HE.T
    Y = OD.reshape(h * w, c).T

    C = np.linalg.lstsq(HE, Y, rcond=None)
    maxC = np.percentile(C[0], 99, axis=1)

    C = C[0] / maxC[:, None]
    C = C * maxCRef[:, None]
    Inorm = Io * np.exp(-np.dot(HERef, C))
    Inorm = Inorm.T.reshape(h, w, c).clip(0, 255).astype("uint8")

    return Inorm


def hematoxylin_eosin_aug(img, low=0.7, high=1.3, seed=None):
    """
    "Quantification of histochemical staining by color deconvolution"
    Arnout C. Ruifrok, Ph.D. and Dennis A. Johnston, Ph.D.
    http://www.math-info.univ-paris5.fr/~lomn/Data/2017/Color/Quantification_of_histochemical_staining.pdf
    Performs random hematoxylin-eosin augmentation
    # Arguments
        img: Numpy image array.
        low: Low boundary for augmentation multiplier
        high: High boundary for augmentation multiplier
    # Returns
        Augmented Numpy image array.
    """
    D = np.array([[1.88, -0.07, -0.60],
                  [-1.02, 1.13, -0.48],
                  [-0.55, -0.13, 1.57]])
    M = np.array([[0.65, 0.70, 0.29],
                  [0.07, 0.99, 0.11],
                  [0.27, 0.57, 0.78]])
    Io = 240

    h, w, c = img.shape
    OD = -np.log10((img.astype("uint16") + 1) / Io)
    C = np.dot(D, OD.reshape(h * w, c).T).T
    r = np.ones(3)
    r[:2] = np.random.RandomState(seed).uniform(low=low, high=high, size=2)
    img_aug = np.dot(C, M) * r

    img_aug = Io * np.exp(-img_aug * np.log(10)) - 1
    img_aug = img_aug.reshape(h, w, c).clip(0, 255).astype("uint8")
    return img_aug


def zoom_aug(img, zoom_var, seed=None):
    """Performs a random spatial zoom of a Numpy image array.
    # Arguments
        img: Numpy image array.
        zoom_var: zoom range multiplier for width and height.
        seed: Random seed.
    # Returns
        Zoomed Numpy image array.
    """
    scale = np.random.RandomState(seed).uniform(
        low=1 / zoom_var, high=zoom_var)
    resized_img = cv2.resize(
        img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return resized_img


def get_crops(img, size, n, seed=None):
    """Creates random square crops of given size from a Numpy image array. No rotation added
    # Arguments
        img: Numpy image array.
        size: size of crops.
        n: number of crops
        seed: Random seed.
    # Returns
        Numpy array of crops, shape (n, size, size, c).
    """
    h, w, c = img.shape
    assert all([size < h, size < w])
    crops = []
    for _ in range(n):
        top = np.random.randint(low=0, high=h - size + 1)
        left = np.random.randint(low=0, high=w - size + 1)
        crop = img[top: top + size, left: left + size].copy()
        crop = np.rot90(crop, np.random.randint(low=0, high=4))
        if np.random.random() > 0.5:
            crop = np.flipud(crop)
        if np.random.random() > 0.5:
            crop = np.fliplr(crop)
        crops.append(crop)

    crops = np.stack(crops)
    assert crops.shape == (n, size, size, c)
    return crops


def gen_crops_with_rotate(img, size, n, seed=None):
    """Creates random square crops of given size from a Numpy image array. With rotation
    # Arguments
        img: Numpy image array.
        size: size of crops.
        n: number of crops
        seed: Random seed.
    # Returns
        Numpy array of crops, shape (n, size, size, c).
    """
    h, w, c = img.shape
    assert all([size < h, size < w])
    d = int(np.ceil(size / np.sqrt(2)))
    crops = []
    for _ in range(n):
        center_y = np.random.randint(low=0, high=h - size + 1) + size // 2
        center_x = np.random.randint(low=0, high=w - size + 1) + size // 2
        m = min(center_y, center_x, h - center_y, w - center_x)
        if m < d:
            max_angle = np.pi / 4 - np.arccos(m / d)
            top = center_y - m
            left = center_x - m
            precrop = img[top: top + 2 * m, left: left + 2 * m]
        else:
            max_angle = np.pi / 4
            top = center_y - d
            left = center_x - d
            precrop = img[top: top + 2 * d, left: left + 2 * d]

        precrop = np.rot90(precrop, np.random.randint(low=0, high=4))
        angle = np.random.uniform(low=-max_angle, high=max_angle)
        precrop = ndimage.rotate(precrop, angle * 180 / np.pi, reshape=False)

        precrop_h, precrop_w, _ = precrop.shape
        top = (precrop_h - size) // 2
        left = (precrop_w - size) // 2
        crop = precrop[top: top + size, left: left + size]

        if np.random.random() > 0.5:
            crop = np.flipud(crop)
        if np.random.random() > 0.5:
            crop = np.fliplr(crop)
        crops.append(crop)

    crops = np.stack(crops)
    assert crops.shape == (n, size, size, c)
    return crops


def norm_pool(features, p=3):
    """Performs descriptor pooling
    # Arguments
        features: Numpy array of descriptors.
        p: degree of pooling.
    # Returns
        Numpy array of pooled descriptor.
    """
    return np.power(np.power(features, p).mean(axis=0), 1 / p)


def encode(crops, model):
    """Encodes crops
    # Arguments
        crops: Numpy array of crops.
        model: Keras encoder.
    # Returns
        Numpy array of pooled descriptor.
    """
    features = model.predict(crops)
    pooled_features = norm_pool(features)
    return pooled_features


def process_image(image_file):
    """Extract multiple crops from a single image
    # Arguments
        image_file: Path to image.
    # Yields
        Numpy array of image crops.
    """
    img = cv2.imread(image_file)
    if SCALE != 1:
        img = cv2.resize(
            img, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_norm = normalize_staining(img)

    for _ in range(AUGMENTATIONS_PER_IMAGE):
        img_aug = hematoxylin_eosin_aug(img_norm, low=COLOR_LO, high=COLOR_HI)
        # img_aug = zoom_aug(img_aug, ZOOM_VAR)

        # single_image_crops = get_crops_free(img_aug, PATCH_SZ,
        # PATCHES_PER_IMAGE)
        single_image_crops = get_crops(img_aug, PATCH_SZ, PATCHES_PER_IMAGE)
        yield single_image_crops


def crops_gen(file_list):
    """Generates batches of crops from image list, one augmentation a time
    # Arguments
        file_list: List of image files.
    # Yields
        Tuple of Numpy array of image crops and name of the file.
    """
    for i, (image_file, output_file) in enumerate(file_list):
        print("Crops generator:", i + 1)
        for crops in process_image(image_file):
            yield crops, output_file


def normalize_stain_to_img(source_path, target_path):
    """
    Normalize source color to be much like target.

    Args:
        @a source/target: two image arrays

    Returns:
        @return: new image which is a tranformed image of @a source, 
            but its color is normalized to be like @a target image.
    """

    source = cv2.cvtColor(cv2.imread(source_path), cv2.COLOR_BGR2LAB)
    target = cv2.cvtColor(cv2.imread(target_path), cv2.COLOR_BGR2LAB)

    # LAB channel means
    src_avg = np.mean(source, axis=(0, 1))
    src_std = np.std(source, axis=(0, 1))

    tar_avg = np.mean(target, axis=(0, 1))
    tar_std = np.std(target, axis=(0, 1))

    assert source.shape[-1] == target.shape[-1], "Source {} and Target {} images have different number of channels.".format(
        source_path, target_path)

    for c in range(source.shape[-1]):
        source[:, :, c] = tar_avg[c] + \
            (source[:, :, c] - src_avg[c]) * (tar_std[c] / src_std[c])

    source = np.clip(source, 0, 255)

    return cv2.cvtColor(source, cv2.COLOR_LAB2RGB)


def norm_stain(image, original):
    image = cv2.cvtColor(cv2.resize(cv2.imread(
        image), (512, 512)), cv2.COLOR_BGR2LAB)
    original = cv2.cvtColor(cv2.resize(cv2.imread(
        original), (512, 512)), cv2.COLOR_BGR2LAB)

    def getavgstd(image):
        avg = []
        std = []
        image_avg_l = np.mean(image[:, :, 0])
        image_std_l = np.std(image[:, :, 0])
        image_avg_a = np.mean(image[:, :, 1])
        image_std_a = np.std(image[:, :, 1])
        image_avg_b = np.mean(image[:, :, 2])
        image_std_b = np.std(image[:, :, 2])
        avg.append(image_avg_l)
        avg.append(image_avg_a)
        avg.append(image_avg_b)
        std.append(image_std_l)
        std.append(image_std_a)
        std.append(image_std_b)
        return (avg, std)

    image_avg, image_std = getavgstd(image)
    original_avg, original_std = getavgstd(original)

    height, width, channel = image.shape
    for i in range(0, height):
        for j in range(0, width):
            for k in range(0, channel):
                t = image[i, j, k]
                t = (t-image_avg[k])*(original_std[k] /
                                      image_std[k]) + original_avg[k]
                t = 0 if t < 0 else t
                t = 255 if t > 255 else t
                image[i, j, k] = t
    image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

    return image


if __name__ == "__main__":

    img_1_path = "/media/bowei/8T/data/ruijin/preprocessed/train/patches/malignant/0_2048/2017-11-26 15_01_15548A_x_3453_y_2048.jpg"
    img_2_path = "/media/bowei/8T/data/ruijin/preprocessed/train/patches/malignant/0_2048/"

    # cv2.imshow(cv2.imread(img_1_path))

    #img_1 = cv2.cvtColor(cv2.imread(img_1_path), cv2.COLOR_BGR2RGB)
    #img_2 = cv2.cvtColor(cv2.imread(img_2_path), cv2.COLOR_BGR2RGB)
    img_1_norm = normalize_staining(img_1_path)
    cv2.imshow("norm_1", img_1_norm)
