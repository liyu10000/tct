def get_cell(box, size, position):
	"""
	cut image out of label box.
	note: label box should be within image
	:params box: (xmin, ymin, xmax, ymax)
	:params size: image size to cut out
	:params position: (x_percent, y_percent), the center of label box relative to image.
					  if need to put label box in center of image, set position to (0.5, 0.5)
	:return: the upper-left coordinates (x, y) of image. if anything wrong happens, return (-1, -1)
	"""
	box_center_x = (box[0]+box[2])//2
	box_center_y = (box[1]+box[3])//2
	x = box_center_x - int(size*position[0])
	y = box_center_y - int(size*position[1])
	if x > box[0] or y > box[1] or x+size < box[2] or y+size < box[3]:
		return (-1, -1)
	return (x, y)
