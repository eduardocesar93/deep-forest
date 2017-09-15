import numpy as np
import tensorflow as tf
import scipy.ndimage
import tifffile
import os
import PIL
import fnmatch
import math
import time

import keras
from keras.models import Sequential
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K

separate_width = 500
length_classification = 20
data_path = "images"
classification_path = "classifiers"

default_graph = tf.get_default_graph()

def current_milli_time():
    return int(round(time.time() * 1000))


def save_image(path, prefix, id):
    """
        Cut and save a tiff image given the image path
        and the prefix ('image', tree_cover').
    """
    image = tifffile.imread(path)
    cut_and_save(data_path, "{0}-{1}".format(prefix, id),
        image, separate_width)


def cut_and_save(directory, name, matrix, length):
    print("{0}/numpy_files/".\
                    format(directory))
    try:
        os.makedirs("{0}/numpy_files/".\
                    format(directory))
    except FileExistsError:
        pass
    limit = max(1, int(len(matrix) / length))
    for i in range(limit):
        for j in range(limit):
            sub_matrix = matrix[i * length : i * length + length,
                                j * length : j * length + length]
            np.save("{0}/numpy_files/{1}-{2}-{3}.npy".\
                    format(data_path, name, i, j),
                    sub_matrix)


def separate_matrix(matrix, length):
    list_matrix = list()
    limit = int(len(matrix) / length)
    for i in range(limit):
        for j in range(limit):
            sub_matrix = matrix[i * length : i * length + length,
                                j * length : j * length + length]
            list_matrix.append(sub_matrix)
    return list_matrix


def find(pattern, path):
    """ Return a list containing all files that matches the pattern in
        a given directory
    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def interpolation(i, j, total_i, total_j, lat_inf, lng_inf, lat_sup, lng_sup):
    int_lat_sup = ((total_i - i) * lat_sup + i * lat_inf) / (total_i)
    int_lat_inf = ((total_i - i - 1)* lat_sup + (i  + 1)* lat_inf) / (total_i)
    int_lng_sup = ((total_j - j) * lng_sup + j * lng_inf) / (total_j)
    int_lng_inf = ((total_j - j - 1)* lng_sup + (j + 1) * lng_inf) / (total_j)

    return {'lat_inf' : int_lat_inf,
            'lng_inf' : int_lng_inf,
            'lat_sup': int_lat_sup,
            'lng_sup': int_lng_sup}


def open_images(id, length, percent=[0,98], label=False, save_tiff=False, map_param=False):
    list_matrix = list()
    prefix = "image" if label == False else "tree_cover"
    total = int(math.sqrt(len(find("{0}-{1}-*".format(prefix, id), \
    "{0}/numpy_files/".format(data_path)))))
    limit_min = int(total * percent[0] * 1.0 / 100)
    limit_max = int(total * percent[1] * 1.0 / 100)

    if save_tiff:
        lat_inf = angle_to_decimal(map_param['lat_inf'])
        lat_sup = angle_to_decimal(map_param['lat_sup'])
        lng_inf = angle_to_decimal(map_param['lng_inf'])
        lng_sup = angle_to_decimal(map_param['lng_sup'])
        try:
            os.makedirs("images/tiff-file/")
        except FileExistsError:
            pass
    for i in range(limit_min, limit_max + 1):
        for j in range(total):
            sub_matrix = \
                np.load("{0}/numpy_files/{1}-{2}-{3}-{4}.npy".\
                        format(data_path, prefix, id, i, j))
            if save_tiff:
                lat_lng = interpolation(i, j, total, total,
                                        lat_inf, lng_inf, lat_sup, lng_sup)
                name = decimal_to_angle(lat_lng['lat_sup']) + '-' + decimal_to_angle(lat_lng['lng_sup'], lat=False) + '__' +\
                       decimal_to_angle(lat_lng['lat_inf']) + '-' + decimal_to_angle(lat_lng['lng_inf'], lat=False) + '.tiff'
                tifffile.imsave('images/tiff-file/' + name, sub_matrix)
            if not label:
                list_matrix += separate_matrix(sub_matrix, length)
            else:
                separate_current_list = \
                    separate_matrix(sub_matrix, length)
                list_matrix.\
                    append([int((np.mean(current_matrix) + 1) / 10)\
                                    for current_matrix \
                                        in separate_current_list])
    return np.array(list_matrix)


def return_feature(directory, name, length, i, j):
    list_features = list()
    sub_matrix = np.load("{0}/numpy_files/{1}/{2}-{3}-{4}.npy".\
                         format(data_path, directory, name, i, j))
    limit = int(len(sub_matrix) / length)
    for u in range(limit):
        for v in range(limit):
            sub_matrix_current =\
                sub_matrix[u * length : u * length + length,
                           v * length : v * length + length]
            mean_colors = sub_matrix_current.mean(0).mean(0)
            var_colors = sub_matrix_current.var(0).var(0)
            list_features.append(mean_colors.tolist()
                                 + var_colors.tolist())
    return list_features


def open_features(directory, name, total, length):
    list_features = list()
    for i in range(total):
        for j in range(total):
            list_features += return_feature(directory,
                                            name, length, i, j)
    return list_features


def classification_criteria(directory, name, length, i, j):
    list_classification = list()
    sub_matrix = np.load("{0}/numpy_files/{1}/{2}-{3}-{4}.npy".\
                         format(data_path, directory, name, i, j))
    limit = int(len(sub_matrix) / length)
    for u in range(limit):
        for v in range(limit):
            sub_matrix_current = \
                sub_matrix[u * length : u * length + length,
                           v * length : v * length + length]
            list_classification.\
                append(int((np.mean(sub_matrix_current) + 1) / 10))
    return list_classification


def open_classifications(directory, name, total, length):
    list_classification = list()
    for i in range(total):
        for j in range(total):
            list_classification += \
                classification_criteria(directory,\
                                        name, length, i, j)
    return list_classification


def success(predicted, result):
    compare = predicted == result
    count_true = 0
    count_false = 0
    for equal in compare:
        if equal:
            count_true += 1
        else:
            count_false += 1
    return count_true / (count_true + count_false)


def angle_to_decimal(angle):
    direction = angle[-1]
    angle = angle[: -1]
    if direction == 'S' or direction == 's' or\
       direction == 'W' or direction == 'w':
        return int(angle) * (-1)
    else:
        return int(angle)

def decimal_to_angle(angle, lat=True):
    if angle >= 0:
        if lat:
            return str(angle) + 'N'
        else:
            return str(angle) + 'E'
    else:
        if lat:
            return str(angle)[1:] + 'S'
        else:
            return str(angle)[1:] + 'W'


def compose_matrix(class_list, image_width):
    limit = int(image_width / length_classification)
    matrix = list()

    for i in range(limit):
        matrix.append(limit * [-1])
    row_block_length = int(separate_width / length_classification)
    num_block_row = int(image_width / separate_width)

    for i in range(len(class_list)):
        block_num = int(i / (row_block_length * row_block_length))
        u = block_num // num_block_row
        v = block_num % num_block_row
        r = i % (row_block_length * row_block_length)
        x = u * row_block_length + r / (row_block_length)
        y = v * row_block_length + r % (row_block_length)
        matrix[int(x)][int(y)] = class_list[i]
    return matrix


def train_classifier(percent_train_min, percent_train_max, percent_test_min,
                     percent_test_max, dataset_id, optimization_method,
                     epochs=1, batch_size=32, activation_function='relu',
                     lr=0.0001):


    with default_graph.as_default():
        ### Open Images #####
        train_data_x = open_images(dataset_id, length_classification, \
            percent=[percent_train_min, percent_train_max])

        test_data_x = open_images(dataset_id, length_classification, \
            percent=[percent_test_min, percent_test_max])

        train_data_y = open_images(dataset_id, length_classification, \
            percent=[percent_train_min, percent_train_max], label = True)

        test_data_y = open_images(dataset_id, length_classification, \
            percent=[percent_test_min, percent_test_max], label = True)


       #### Aplying classifier #####
        activation = activation_function
        batch_size = batch_size,
        lr = lr
        num_classes = 11
        epochs = epochs
        data_augmentation = True

        # The data, shuffled and split between train and test sets:
        print('x_train shape:', train_data_x.shape)
        print(train_data_x.shape[0], 'train samples')
        print(test_data_x.shape[0], 'test samples')

        # Convert class vectors to binary class matrices.
        train_data_y = keras.utils.\
            to_categorical(train_data_y, num_classes)
        test_data_y = keras.utils.\
            to_categorical(test_data_y, num_classes)

        model = Sequential()

        model.add(Conv2D(32,  (3, 3), padding='same',
                        input_shape=train_data_x.shape[1:]))
        model.add(Activation(activation_function))
        model.add(Conv2D(32, (3, 3)))
        model.add(Activation(activation_function))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (3, 3), padding='same'))
        model.add(Activation(activation_function))
        model.add(Conv2D(64, (3, 3)))
        model.add(Activation(activation_function))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation(activation_function))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes))
        model.add(Activation('softmax'))

        # initiate RMSprop optimizer
        if int(optimizer) == 1:
            opt = keras.optimizers.Adadelta(lr=lr, decay=1e-6)
        elif int(optimizer) == 2:
            opt = keras.optimizers.SGD(lr=lr, decay=1e-6)
        elif int(optimizer) == 3:
            opt = keras.optimizers.Adagrad(lr=lr, decay=1e-6)
        else:
            opt = keras.optimizers.rmsprop(lr=lr, decay=1e-6)

        # Let's train the model using RMSprop
        model.compile(loss='categorical_crossentropy',
                     optimizer=opt, metrics=['accuracy'])


        if not data_augmentation:
            print('Not using data augmentation.')
        else:
            print('Using real-time data augmentation.')

            # This will do preprocessing and realtime data augmentation:
            datagen = ImageDataGenerator(
                featurewise_center=False,
                samplewise_center=False,
                featurewise_std_normalization=False,
                samplewise_std_normalization=False,
                zca_whitening=False,
                rotation_range=0,
                width_shift_range=0.1,
                height_shift_range=0.1,
                horizontal_flip=True,
                vertical_flip=False)

            # Compute quantities required for feature-wise normalization
            datagen.fit(train_data_x)

            # Fit the model on the batches generated by datagen.flow().
            model.fit_generator\
                 (datagen.flow(train_data_x, train_data_y, batch_size=batch_size), steps_per_epoch=train_data_x.shape[0] // batch_size, epochs=epochs,  validation_data=(test_data_x, test_data_y))
            score = model.evaluate(test_data_x, test_data_y, verbose=0)

            ## Persist classifier ##

            current_time = current_milli_time()
            try:
                 os.makedirs("{0}/".format(classification_path))
            except FileExistsError:
                pass
            model_path = './' + classification_path + '/' + str(current_time) + '.h5'
            model.save(model_path)


        # print('Test loss:', score[0])
        # print('Test accuracy:', score[1]

    return score, model_path


def classify_images(model_path, data_set_id_first, data_set_id_last):
    print("---Loading the model---")
    print("---Model loaded---")
    print("---Opening Images---")
    first_image_list = open_images(int(data_set_id_first), length_classification)
    last_image_list = open_images(int(data_set_id_last), length_classification)
    print("---Predicting---")
    with tf.Session(graph=default_graph) as session:
        init = tf.global_variables_initializer()
        session.run(init)
        classifier = load_model(model_path)
        forestation_level_first = classifier.predict(first_image_list)
        forestation_level_last = classifier.predict(last_image_list)
    first_image_list = None
    last_image_list = None
    deforestation_labels = list()

    for i in range(len(forestation_level_first)):
        label_returned = -1
        prob_returned = -1
        deforestation_labels.append(define_discrete_label(forestation_level_first[i]) -\
            define_discrete_label(forestation_level_last[i]))
    total_class_width = math.sqrt(len(deforestation_labels))
    print("---Composing Matrix---")
    return compose_matrix(deforestation_labels, total_class_width * length_classification)

def define_discrete_label(probs):
    returned_label = -1
    returned_prob = -1
    for i in range(11):
        if probs[i] > returned_prob:
            returned_label = i
            returned_prob = probs[i]
    return returned_label

#train_classifier(41, 43, 55, 57, 1, 20)
#train_classifier(41, 57, 53, 61, 1, 20)
#list = open_images(3, 20)
#print ("{} {} {}".format(len(list), len(list[0]), len(list[0][0])))

#utils.open_images(7, 20, label=False, save_tiff=True, map_param={'lat_sup': '0N', 'lng_sup': '70W', 'lat_inf':'10S', 'lng_inf':'60W'})
