"""
Train patch classification by a pre-trained CNN architecture. 
Fine-tuning is applied since data size is limited.
"""
import os
import csv
import numpy as np
from os.path import join as pjoin
from keras import optimizers
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from keras.callbacks import ModelCheckpoint
from keras.callbacks import TensorBoard
import time
import cv2

from config import *
import utils


def preprocess_2_gray(x):
    """"""
    gray_x = cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
    rgb_x = cv2.cvtColor(gray_x, cv2.COLOR_GRAY2BGR)

    return preprocess_input(rgb_x)


def get_base_model(mode="inception", pretrained=True):
    """
    Get the base pre-trained model we will use
    """
    base_model = None

    if mode == "inception":
        if pretrained:
            base_model = InceptionV3(weights='imagenet', include_top=False)
        else:
            base_model = InceptionV3(weights=None, include_top=False)

    else:
        assert False, "Base model with mode {} not supported.".format(mode)

    return base_model


def get_base_empty_model():
    return InceptionV3(weights=None, include_top=False)


def add_fc_layer(base_model, num_classes):
    """
    Function to add a final fully connected block on top of @arg base_model.
    The block contains one global average pooling follows by 
    """
    # add a global spatial average pooling layer
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    # let's add a fully-connected layer
    x = Dense(TOP_FC_SIZE, activation='relu')(x)
    # and a logistic layer -- we have 2 classes
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    return model


def get_model(num_classes, mode, pretrained):

    base_model = get_base_model(mode, pretrained)
    return add_fc_layer(base_model, num_classes)


def log_data_info(data_dir, logger):
    """
    Log number of samples in @arg data_dir for each type.
    Return the number of samples in data_dir.
    """
    type_names = [dI for dI in os.listdir(
        data_dir) if os.path.isdir(pjoin(data_dir, dI))]

    total_sample_num = 0

    for cls_name in type_names:
        cls_dir = pjoin(data_dir, cls_name)
        cls_num = utils.count_files(cls_dir, ".jpg")

        logger.info("Samples num of class {}: {}.".format(cls_name, cls_num))

        total_sample_num += cls_num

    return total_sample_num


def get_train_data_generator(data_dir, logger, save=False):
    """
    Function to return data generators for train and valid data sets.
    """
    train_dir = pjoin(data_dir, "train")
    valid_dir = pjoin(data_dir, "valid")

    logger.info("Summarizing sample info in train set.")

    train_num = log_data_info(train_dir, logger)
    logger.info("Summarizing sample info in valid set.")
    valid_num = log_data_info(valid_dir, logger)

    logger.info("Total number of training data: {}; Total number of validation data: {}.".format(
        train_num, valid_num))

    # prepare data augmentation configuration
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=30,      # 图片随机转动的角度
        width_shift_range=0.2,  # 图片随机水平偏移的幅度
        height_shift_range=0.2, # 图片随机竖直偏移的幅度
        shear_range=0.2,        # 逆时针方向的剪切变换角度
        zoom_range=0.2,         # 随机缩放的幅度
        horizontal_flip=True,   # 随机水平翻转
        vertical_flip=True      # 随机竖直翻转
    )

    valid_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    save_dir = None
    if save:
        save_dir = pjoin(data_dir, "gen_train")
        utils.mkdirs(save_dir)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=PATCH_BATCH_SIZE,
        class_mode='categorical',
        save_to_dir=save_dir
    )

    valid_generator = valid_datagen.flow_from_directory(
        valid_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=PATCH_BATCH_SIZE,
        class_mode='categorical')

    return (train_generator, train_num), (valid_generator, valid_num)


def get_test_data_generator(data_dir, logger):
    """
    Function to return data generators for test data sets.
    """
    test_dir = pjoin(data_dir, "test")

    logger.info("Summarizing sample info in test set.")
    test_num = log_data_info(test_dir, logger)

    logger.info("Total number of test data: {}.".format(test_num))

    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=PATCH_BATCH_SIZE,
        class_mode='categorical',
        shuffle=False)

    return (test_generator, test_num)


def train_top_layer_only(base_model, model, train_generator_tuple, valid_generator_tuple, cp_path, logger):
    """
    Train only top layer
    """

    train_generator, train_num = train_generator_tuple
    valid_generator, valid_num = valid_generator_tuple

    if os.path.exists(cp_path):
        model.load_weights(cp_path)
        logger.info("Checkpoint '" + cp_path + "' loaded.")

    # first: train only the top layers (which were randomly initialized)
    # i.e. freeze all convolutional InceptionV3 layers
    for layer in base_model.layers:
        layer.trainable = False

    adam = optimizers.Adam(lr=TOP_LAYER_LR)
    # compile the model (should be done *after* setting layers to non-trainable)
    model.compile(optimizer=adam, loss="categorical_crossentropy",
                  metrics=["accuracy"])

    # Save the model after every epoch.
    mc_top = ModelCheckpoint(cp_path, monitor='val_acc', verbose=1,
                             save_best_only=SAVE_BEST_ONLY, save_weights_only=False, mode='auto', period=1)

    # Save the TensorBoard logs.
    # tb = TensorBoard(log_dir=LOG_DIR, histogram_freq=0, write_graph=True, write_images=True)

    # train the model on the new data for a few epochs
    # model.fit_generator(...)

    train_hist = model.fit_generator(
        train_generator,
        steps_per_epoch=train_num // PATCH_BATCH_SIZE,
        epochs=TOP_EPOCH,
        validation_data=valid_generator,
        validation_steps=valid_num // PATCH_BATCH_SIZE,
        callbacks=[mc_top])

    return train_hist


def train_top_inception_blocks(base_model, model, train_generator_tuple, valid_generator_tuple, cp_path, logger):

    train_generator, train_num = train_generator_tuple
    valid_generator, valid_num = valid_generator_tuple

    if os.path.exists(cp_path):
        model.load_weights(cp_path)
        logger.info("Checkpoint '" + cp_path + "' loaded.")

    # Save the model after every epoch.
    mc_fit = ModelCheckpoint(cp_path, monitor='val_acc', verbose=1,
                             save_best_only=SAVE_BEST_ONLY, save_weights_only=False, mode='auto', period=1)

    # # we chose to train the top 5 inception blocks, i.e. we will freeze
    # # the first 133 layers and unfreeze the rest.
    # for layer in model.layers[:133]:
    #    layer.trainable = False
    # for layer in model.layers[133:]:
    #    layer.trainable = True

    for layer in model.layers:
        layer.trainable = True

    # we need to recompile the model for these modifications to take effect
    # we use SGD with a low learning rate
    adam = optimizers.Adam(lr=FINE_TUNE_LR)
    model.compile(optimizer=adam, loss='categorical_crossentropy',
                  metrics=['accuracy'])

    # we train our model again (this time fine-tuning the top 2 inception blocks
    # alongside the top Dense layers
    # model.fit_generator(...)

    train_hist = model.fit_generator(
        train_generator,
        steps_per_epoch=train_num // PATCH_BATCH_SIZE,
        epochs=FINE_TUNE_EPOCH,
        validation_data=valid_generator,
        validation_steps=valid_num // PATCH_BATCH_SIZE,
        callbacks=[mc_fit])

    return train_hist


def train_from_scratch(model, train_generator_tuple, valid_generator_tuple, cp_path, logger):
    train_generator, train_num = train_generator_tuple
    valid_generator, valid_num = valid_generator_tuple

    if os.path.exists(cp_path):
        model.load_weights(cp_path)
        logger.info("Checkpoint '" + cp_path + "' loaded.")

    # Save the model after every epoch.
    mc_fit = ModelCheckpoint(cp_path, monitor='val_acc', verbose=1,
                             save_best_only=SAVE_BEST_ONLY, save_weights_only=False, mode='auto', period=1)

    # we chose to train the top 5 inception blocks, i.e. we will freeze
    # the first 133 layers and unfreeze the rest.
    for layer in model.layers:
        layer.trainable = True

    # we need to recompile the model for these modifications to take effect
    # we use SGD with a low learning rate
    adam = optimizers.Adam(lr=TRAIN_FROM_SCRATCH_LR)
    model.compile(optimizer=adam, loss='categorical_crossentropy',
                  metrics=['accuracy'])

    # we train our model again (this time fine-tuning the top 2 inception blocks
    # alongside the top Dense layers
    # model.fit_generator(...)

    train_hist = model.fit_generator(
        train_generator,
        steps_per_epoch=train_num // PATCH_BATCH_SIZE,
        epochs=TRAIN_EPOCH,
        validation_data=valid_generator,
        validation_steps=valid_num // PATCH_BATCH_SIZE,
        callbacks=[mc_fit])

    return train_hist


def save_hist(hist, save_path, logger, method="json"):
    """
    Function to save Keras's Callback.History object to @arg save_path.
    """

    hist_dict = hist.history

    with open(save_path, 'w') as f:
        if method == "json":
            import json
            json.dump(hist_dict, f)
        elif method == "pickle":
            import pickle
            pickle.dump(hist_dict, f)
        else:
            logger.error("Undefined save method for function save_path.")


def evaluate_on(model, data_gen):
    """"""
    model.compile(optimizer="adam",
                  loss='categorical_crossentropy', metrics=['accuracy'])

    return model.evaluate_generator(data_gen)


def train():

    logger = utils.setup_logger(LOG_DIR, "train_inception_fix_"+class_type, save_log=True)

    utils.mkdirs([LOG_DIR, MODEL_CP_DIR])

    # paths to save checkpoint weights
    top_layers_checkpoint_path = pjoin(MODEL_CP_DIR, "cp.top.best.hdf5")
    fine_tuned_checkpoint_path = pjoin(
        MODEL_CP_DIR, "cp.fine_tuned.weights.{epoch:02d}-{val_acc:.4f}.hdf5")
    train_checkpoint_path = pjoin(
        MODEL_CP_DIR, "cp.train.weights.{epoch:02d}-{val_acc:.4f}.hdf5")
    new_complete_inception_weights = pjoin(
        MODEL_CP_DIR, "cp.fine_tuned.final_weights.hdf5")

    # get train/valid data generators
    logger.info(
        "[DATA GENERATOR] Getting data generators for train/valid set.")
    train_generator_tuple, valid_generator_tuple = get_train_data_generator(
        PATCH_ARR_DIR, logger, save=False)

    # get model
    base_model = get_base_empty_model()
    # base_model = get_base_model()
    model = add_fc_layer(base_model, NUM_CLASSES)

    # # train top layer for some epochs
    # logger.info("[TOP LAYER] Start training for top layer.")
    # t_top = time.time()
    # top_train_hist = train_top_layer_only(base_model, model, train_generator_tuple, valid_generator_tuple, top_layers_checkpoint_path, logger)
    # save_hist(top_train_hist, pjoin(LOG_DIR, "top_hist.json"), method="json")

    # logger.info("[TOP LAYER] Training for top layer done in {}s.".format(time.time() - t_top))

    # # load best training result for top layer's training
    # if os.path.exists(top_layers_checkpoint_path):
    #     model.load_weights(top_layers_checkpoint_path)
    #     logger.info("Checkpoint '" + top_layers_checkpoint_path + "' loaded.")

    # # fine-tune weights for some more layers
    # t_finetune = time.time()
    # logger.info("[FINE TUNE] Start fine-tuning.")
    # tune_train_hist = train_top_inception_blocks(base_model, model, train_generator_tuple, valid_generator_tuple, fine_tuned_checkpoint_path, logger)

    # save_hist(tune_train_hist, pjoin(LOG_DIR, "fine_tune_hist.json"), logger, method="json")
    # logger.info("[FINE TUNE] Fine-tuning done in {}s.".format(time.time() - t_top))

    # fine-tune weights for some more layers
    t_train = time.time()
    logger.info("[TRAIN SCRATCH] Start training from scratch.")
    train_hist = train_from_scratch(
        model, train_generator_tuple, valid_generator_tuple, train_checkpoint_path, logger)

    save_hist(train_hist, pjoin(LOG_DIR, "train_hist.json"),
              logger, method="json")
    logger.info("[TRAIN SCRATCH] Training from scratch with {} epochs done in {}s.".format(
        TRAIN_EPOCH, time.time() - t_train))

    # save final weight
    model.save_weights(new_complete_inception_weights)


def test():
    logger = utils.setup_logger(LOG_DIR, 'train_inception_fix_'+class_type, save_log=True)

    base_model = get_base_empty_model()
    model = add_fc_layer(base_model, NUM_CLASSES)
    model.load_weights(pjoin(MODEL_CP_DIR, 'cp.train.weights.41-0.7181.hdf5'))

    test_generator, _ = get_test_data_generator(PATCH_ARR_DIR, logger)

    steps = len(test_generator)
    # score = evaluate_on(model,test_generator)
    # print('loss:' ,score[0],'accuracy:',score[1])
    y_pred = model.predict_generator(test_generator, use_multiprocessing=True, verbose=1, steps=steps)

    results = []
    for step in range(steps):
        y = test_generator[step][1]
        print(y)
        for i,y_i in enumerate(y):
            results.append([np.argmax(y_i)] + y_pred[step*PATCH_BATCH_SIZE+i].tolist())

    with open("results.csv", "w") as f:
        csv_writer = csv.writer(f)
        for r in results:
            csv_writer.writerow(r)
            
    return results




if __name__ == "__main__":
    # train()
    test()