# importing the module 
import cv2
import numpy as np
import os
# function to display the coordinates of 
# of the points clicked on the image 
# exec(open(r'ler_xy.py').read())

#IMAGEM = 'DJI_0723_rosa.jpg'
# mascara_baixo = [130,0,220] # branco: [0, 0, 255 - tolerancia] - rosa: [130,0,220]
# mascara_cima = [170,255,255] # branco: [255, tolerancia, 255] - rosa: [170,255,255]

tolerancia = 20
mascara_baixo = [0, 0, 255 - tolerancia] # branco: [0, 0, 255 - tolerancia] - rosa: [130,0,220]
mascara_cima = [255, tolerancia, 255]  # branco: [255, tolerancia, 255] - rosa: [170,255,255]

def abrir_imagem(IMAGEM_NOME, CAMINHO, PTO_CONTROLE, rel_x=None, rel_y=None):
	IMAGEM = os.path.join(CAMINHO, IMAGEM_NOME)
	TITULO = IMAGEM + ' - GPC # ' + str(PTO_CONTROLE)
	coord = [0, 0]
	incrementos_shift = 100
	percent_scale = 100
	hor_shift = 0
	ver_shift = 0
	is_mask = False
	if rel_x is not None and rel_y is not None:
		rel_x = float(rel_x)
		rel_y = float(rel_y)

	def click_event(event, x, y, flags, params): 
		nonlocal coord
		# Ignore clicks if rel_x and rel_y are provided
		if rel_x is not None and rel_y is not None:
			return 
		# checking for left mouse clicks 
		if event == cv2.EVENT_LBUTTONDOWN:

			# displaying the coordinates 
			# on the Shell 
			# print(x, ' ', y) 

			# displaying the coordinates 
			# on the image window 
			font = cv2.FONT_HERSHEY_SIMPLEX 
			cv2.putText(img,
								str(int(x / (percent_scale / 100) - hor_shift)) +
								',' +
								str(int(y / (percent_scale / 100) - ver_shift)),
						(int(x / (percent_scale / 100) - hor_shift),int(y / (percent_scale / 100) - ver_shift)), font, 
						1, (255, 0, 0), 2)
			width = int(img.shape[1] * percent_scale / 100)
			height = int(img.shape[0] * percent_scale / 100)
			dim = (width, height)
			M = np.float32([
					[1, 0, hor_shift * percent_scale / 100],
					[0, 1, ver_shift * percent_scale / 100]
				])
			resized_im = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
			shifted = cv2.warpAffine(resized_im, M, (resized_im.shape[1], resized_im.shape[0]))
			if rel_x is not None and rel_y is not None:
				circle_radius = int(min(img.shape[0], img.shape[1]) * 0.025)  # 5% diameter = 2.5% radius
				cv2.circle(resized, (int(rel_x * percent_scale / 100), int(rel_y * percent_scale / 100)), circle_radius, (0, 255, 0), 2)
				# Draw
				crosshair_length = circle_radius
				center_x = int(rel_x * percent_scale / 100)
				center_y = int(rel_y * percent_scale / 100)
				cv2.line(resized, (center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y), (0, 255, 0), 2)
				cv2.line(resized, (center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length), (0, 255, 0), 2)
			cv2.imshow(TITULO, shifted)
			coord=[str(int(x / (percent_scale / 100) - hor_shift)), str(int(y / (percent_scale / 100) - ver_shift))]

	# def write_file():
	# 		nonlocal coord
	# 		print(coord)
	# 		f = open("teste.txt", "a+")
	# 		f.write(str(coord[0]) + '\t'  + str(coord[1]) + '\n')
	# 		f.close()
	# 		return None

	def zoom_image(sentido):
		nonlocal percent_scale, hor_shift, ver_shift
		if sentido == 'out':
			if percent_scale < 25:
				return None
			percent_scale = percent_scale - 10
			hor_shift = hor_shift * 0.8
			ver_shift = ver_shift * 0.8
		if sentido == 'in':
			if percent_scale > 500:
					return None
			hor_shift = hor_shift * 1.2
			ver_shift = ver_shift * 1.2
			percent_scale = percent_scale + 10
		width = int(img.shape[1] * percent_scale / 100)
		height = int(img.shape[0] * percent_scale / 100)
		dim = (width, height)
		
		M = np.float32([
				[1, 0, hor_shift * percent_scale / 100],
				[0, 1, ver_shift * percent_scale / 100]
			])
		resized_im = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		shifted = cv2.warpAffine(resized_im, M, (resized_im.shape[1], resized_im.shape[0]))
		if rel_x is not None and rel_y is not None:
			circle_radius = int(min(img.shape[0], img.shape[1]) * 0.025)  # 5% diameter = 2.5% radius
			cv2.circle(resized, (int(rel_x * percent_scale / 100), int(rel_y * percent_scale / 100)), circle_radius, (0, 255, 0), 2)
			# Draw
			crosshair_length = circle_radius
			center_x = int(rel_x * percent_scale / 100)
			center_y = int(rel_y * percent_scale / 100)
			cv2.line(resized, (center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y), (0, 255, 0), 2)
			cv2.line(resized, (center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length), (0, 255, 0), 2)
		cv2.imshow(TITULO, shifted)
		if is_mask:
				apply_mask(True)

	def shift_image(sentido):
			nonlocal hor_shift, ver_shift
			if sentido == 'down':
					ver_shift -= incrementos_shift
			if sentido == 'up':
					ver_shift += incrementos_shift
			if sentido == 'left':
					hor_shift += incrementos_shift
			if sentido == 'right':
					hor_shift -= incrementos_shift
			width = int(img.shape[1] * percent_scale / 100)
			height = int(img.shape[0] * percent_scale / 100)
			dim = (width, height)
			M = np.float32([
				[1, 0, hor_shift * percent_scale / 100],
				[0, 1, ver_shift * percent_scale / 100]
			])
			resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
			shifted = cv2.warpAffine(resized, M, (resized.shape[1], resized.shape[0]))
			# If rel_x and rel_y are provided, draw circle with crosshair in the middle
			if rel_x is not None and rel_y is not None:
				circle_radius = int(min(img.shape[0], img.shape[1]) * 0.025)  # 5% diameter = 2.5% radius
				cv2.circle(resized, (int(rel_x * percent_scale / 100), int(rel_y * percent_scale / 100)), circle_radius, (0, 255, 0), 2)
				# Draw
				crosshair_length = circle_radius
				center_x = int(rel_x * percent_scale / 100)
				center_y = int(rel_y * percent_scale / 100)
				cv2.line(resized, (center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y), (0, 255, 0), 2)
				cv2.line(resized, (center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length), (0, 255, 0), 2)
			cv2.imshow(TITULO, shifted)
			if is_mask:
					apply_mask(True)

	def apply_mask(keep_mask = False):
			nonlocal is_mask
			width = int(img.shape[1] * percent_scale / 100)
			height = int(img.shape[0] * percent_scale / 100)
			dim = (width, height)
			M = np.float32([
				[1, 0, hor_shift * percent_scale / 100],
				[0, 1, ver_shift * percent_scale / 100]
			])
			resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
			shifted = cv2.warpAffine(resized, M, (resized.shape[1], resized.shape[0]))
			if is_mask and not keep_mask:
				cv2.imshow(TITULO, shifted)
				is_mask = False
				return None
			hsv = cv2.cvtColor(shifted, cv2.COLOR_BGR2HSV)
			mask = cv2.inRange(hsv, np.array(mascara_baixo), np.array(mascara_cima)) 
			result = cv2.bitwise_and(shifted,shifted, mask= mask)
			cv2.imshow(TITULO, result)
			is_mask = True

	# driver function 

	# reading the image 
	img = cv2.imread(IMAGEM, 1) 
	width = int(img.shape[1] * percent_scale / 100)
	height = int(img.shape[0] * percent_scale / 100)
	dim = (width, height)

	# resize image
	resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

	# If rel_x and rel_y are provided, draw circle with crosshair in the middle
	if rel_x is not None and rel_y is not None:
		circle_radius = int(min(img.shape[0], img.shape[1]) * 0.025)  # 5% diameter = 2.5% radius
		cv2.circle(resized, (int(rel_x * percent_scale / 100), int(rel_y * percent_scale / 100)), circle_radius, (0, 255, 0), 2)
		# Draw
		crosshair_length = circle_radius
		center_x = int(rel_x * percent_scale / 100)
		center_y = int(rel_y * percent_scale / 100)
		cv2.line(resized, (center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y), (0, 255, 0), 2)
		cv2.line(resized, (center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length), (0, 255, 0), 2)

	# displaying the image 
	# cv2.namedWindow(TITULO, cv2.WINDOW_NORMAL)
	cv2.imshow(TITULO, resized)
	# setting mouse handler for the image 
	# and calling the click_event() function 
	cv2.setMouseCallback(TITULO, click_event) 

	# wait for a key to be pressed to exit 
	key = -1

	while key != ord('s') and key != ord('S'):
		key = cv2.waitKey(33)
		if key == ord('-'):
				zoom_image('out')
		if key == ord('+'):
				zoom_image('in')
		if key == ord('k') or key == ord('K'):
				shift_image('down')
		if key == ord('i') or key == ord('I'):
				shift_image('up')
		if key == ord('l') or key == ord('L'):
				shift_image('right')
		if key == ord('j') or key == ord('J'):
				shift_image('left')
		if key == ord('m') or key == ord('M'):
				apply_mask()
		if key == ord('z') or key == ord('Z'):
				coord = [0, 0]
				img = cv2.imread(IMAGEM, 1)
				width = int(img.shape[1] * percent_scale / 100)
				height = int(img.shape[0] * percent_scale / 100)
				dim = (width, height)
				M = np.float32([
					[1, 0, hor_shift * percent_scale / 100],
					[0, 1, ver_shift * percent_scale / 100]
				])
				resized_im = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
				shifted = cv2.warpAffine(resized_im, M, (resized_im.shape[1], resized_im.shape[0]))
				if rel_x is not None and rel_y is not None:
					circle_radius = int(min(img.shape[0], img.shape[1]) * 0.025)  # 5% diameter = 2.5% radius
					cv2.circle(resized, (int(rel_x * percent_scale / 100), int(rel_y * percent_scale / 100)), circle_radius, (0, 255, 0), 2)
					# Draw
					crosshair_length = circle_radius
					center_x = int(rel_x * percent_scale / 100)
					center_y = int(rel_y * percent_scale / 100)
					cv2.line(resized, (center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y), (0, 255, 0), 2)
					cv2.line(resized, (center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length), (0, 255, 0), 2)
				cv2.imshow(TITULO, shifted)
				if is_mask:
					apply_mask(True)
	
 	# close the window 
	cv2.destroyAllWindows() 

	return coord