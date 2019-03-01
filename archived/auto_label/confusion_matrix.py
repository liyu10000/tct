import os
import numpy as np
import xlsxwriter

def confusion_matrix(classes, cell_numpy_index, predictions):
	"""
	classes: ("ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", "MC", "RC", "SC", "SCC", "TRI", "VIRUS")
	cell_numpy_index: {index:(x_y_i, class_i)}
	predictions: numpy array
	return: confusion matrix
	"""
	matrix_sum = [[0 for x in range(len(classes))] for y in range(len(classes))]
	index = 0
	for prediction in predictions:
		i = np.argmax(prediction)
		class_i_predict = classes[i]
		class_i_original = cell_numpy_index[index][1]
		matrix_sum[classes.index(class_i_original)][classes.index(class_i_predict)] += 1
		index += 1
	matrix_acc = [[0.0 for x in range(len(classes))] for y in range(len(classes))]
	for i in range(len(classes)):
		sum_i = sum(matrix_sum[i])
		if sum_i == 0:
			continue
		for j in range(len(classes)):
			matrix_acc[i][j] = matrix_sum[i][j] / sum_i
	return matrix_acc

def generate_xlsx(classes, matrix, xlsx):
	"""
	classes: ("ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", "MC", "RC", "SC", "SCC", "TRI", "VIRUS")
	matrix: confusion matrix
	xlsx: xlsx full path name
	"""
	workbook = xlsxwriter.Workbook(xlsx)
	worksheet = workbook.add_worksheet()
	for i in range(len(classes)):
		worksheet.write(0,i+1,classes[i])
	for i in range(len(classes)):
		worksheet.write(i+1,0,classes[i])
		for j in range(len(classes)):
			worksheet.write(i+1,j+1,matrix[i][j])
	workbook.close()
