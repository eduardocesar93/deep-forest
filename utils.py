import numpy as np
import tensorflow
import scipy.ndimage
import tifffile 
import os
import matplotlib.pyplot as plt
import PIL


separate_width = 500 
length_classification = 20
data_path = "images"


def save_image(path, prefix, id):
    """
        Cut and save a tiff image given the image path
        and the prefix ('image', tree_cover').
    """
    image = tifffile.imread(path)
    cut_and_save(data_path, "{0}-{1}".format(prefix, id), image, separate_width)


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


def open_images(directory, name, total, length,
                percent=[0,100], label=False):
    list_matrix = list()
    limit_min = int(total * percent[0] * 1.0 / 100)
    limit_max = int(total * percent[1] * 1.0 / 100)
    for i in range(limit_min, limit_max):
        for j in range(total):
            sub_matrix = \
                np.load("{0}/numpy_files/{1}/{2}-{3}-{4}.npy".\
                        format(data_path, directory, name, i, j))
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


def compose_matrix(class_list, image_width,
                   separate_width, length_classification):
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