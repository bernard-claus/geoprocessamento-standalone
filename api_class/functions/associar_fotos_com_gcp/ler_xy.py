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

def abrir_imagem(IMAGEM_NOME, CAMINHO, PTO_CONTROLE, rel_x=None, rel_y=None, no_return=False):
	IMAGEM = os.path.join(CAMINHO, IMAGEM_NOME)
	TITULO = IMAGEM + ' - GPC # ' + str(PTO_CONTROLE)
	coord = [0, 0]
	panning = False
	panning_x, panning_y = 0, 0
	incrementos_shift = 100
	percent_scale = 100
	hor_shift = 0
	ver_shift = 0
	last_x = 0
	last_y = 0
	is_mask = False
	if rel_x is not None and rel_y is not None:
		rel_x = float(rel_x)
		rel_y = float(rel_y)

	print(rel_x, rel_y)

	def draw_pointer(x, y, image, scale=1.0, color=(0, 255, 0)):
		# Draws a circle and crosshair at (x, y) on the given image
		print('on draw x/y: ', x, y)
		h, w = image.shape[:2]
		circle_radius = 100
		center_x = int(x * scale)
		center_y = int(y * scale)
		cv2.circle(image, (center_x, center_y), circle_radius, color, 2)
		crosshair_length = circle_radius
		crosshair_length = 25  # 50 pixels total (25 on each side)
		cv2.line(image, (center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y), color, 1)
		cv2.line(image, (center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length), color, 1)

	def mouse_event(event, x, y, flags, params): 
		nonlocal coord, hor_shift, ver_shift, percent_scale, last_x, last_y, window_width, window_height, panning_x, panning_y, panning
  
		# checking for left mouse clicks 
		if event == cv2.EVENT_LBUTTONDOWN:
			if no_return:
				return
			
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
				draw_pointer(rel_x, rel_y, shifted, scale=1.0, color=(0, 255, 0))
			cv2.imshow(TITULO, shifted)
			coord=[str(int(x / (percent_scale / 100) - hor_shift)), str(int(y / (percent_scale / 100) - ver_shift))]
   
   
		# TODO: Fix MOUSEWHEEL and RBUTTONDOWN functionalities
		elif event == cv2.EVENT_MOUSEWHEEL:
			# Get mouse position in original image coordinates before zoom
			x = last_x
			y = last_y

			mouse_img_x = x / (percent_scale / 100) - hor_shift
			mouse_img_y = y / (percent_scale / 100) - ver_shift
			
			old_percent_scale = percent_scale
			
			if flags > 0:  # Scroll up - zoom in
				if percent_scale < 500:
					percent_scale = percent_scale + 10
			else:  # Scroll down - zoom out
				if percent_scale > 25:
					percent_scale = percent_scale - 10
   
			# hor_shift -= x * ((percent_scale / 100) - 1)
			# ver_shift -= y * ((percent_scale / 100) - 1)
			hor_shift = x / (percent_scale / 100) - mouse_img_x
			ver_shift = y / (percent_scale / 100) - mouse_img_y
			
			# Redraw
			width = int(img.shape[1] * percent_scale / 100)
			height = int(img.shape[0] * percent_scale / 100)
			dim = (width, height)
			total_horizontal_shift = hor_shift * percent_scale / 100
			total_vertical_shift = ver_shift * percent_scale / 100

			current_image_width = img.shape[1] * percent_scale / 100
			current_image_height = img.shape[0] * percent_scale / 100
     
			# cima e esquerda: shift não pode ser negativo
			# direita e baixo: shift + tamanho da imagem não pode ser menor que tamanho janela  
			if flags < 0:
				if current_image_width + total_horizontal_shift < window_width:
					offset = window_width - (current_image_width + total_horizontal_shift)
					total_horizontal_shift += offset
				if current_image_height + total_vertical_shift < window_height:
					offset = window_height - (current_image_height + total_vertical_shift)
					total_vertical_shift += offset
     
				if total_horizontal_shift > 0:
					total_horizontal_shift = 0
				if total_vertical_shift > 0:
					total_vertical_shift = 0
    
				if current_image_width <= window_width:
					total_horizontal_shift = 0
				if current_image_height <= window_width:
					total_vertical_shift = 0

			hor_shift = total_horizontal_shift / (percent_scale / 100)
			ver_shift = total_vertical_shift / (percent_scale / 100)
   
			M = np.float32([
				[1, 0, total_horizontal_shift],
				[0, 1, total_vertical_shift]
			])
			resized_im = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
			shifted = cv2.warpAffine(resized_im, M, (resized_im.shape[1], resized_im.shape[0]))
			if rel_x is not None and rel_y is not None:
				draw_pointer(rel_x + hor_shift, rel_y + ver_shift, shifted, scale=percent_scale/100, color=(0, 255, 0))
			cv2.imshow(TITULO, shifted)
			if is_mask:
				apply_mask(True)

		# Pan
		elif event == cv2.EVENT_RBUTTONDOWN:
			# Get the current window size and calculate center
			panning = True
			panning_x = x
			panning_y = y

			# # Calculate the actual coordinates in the original image
			# actual_x = int(x / (percent_scale / 100) - hor_shift)
			# actual_y = int(y / (percent_scale / 100) - ver_shift)

			# # Calculate new shifts to center the clicked point
			# hor_shift = (window_width / 2) / (percent_scale / 100) - actual_x
			# ver_shift = (window_height / 2) / (percent_scale / 100) - actual_y

			# # Redraw the image with new shifts
			# width = int(img.shape[1] * percent_scale / 100)
			# height = int(img.shape[0] * percent_scale / 100)
			# dim = (width, height)
			# M = np.float32([
			# 	[1, 0, hor_shift * percent_scale / 100],
			# 	[0, 1, ver_shift * percent_scale / 100]
			# ])
			# resized_im = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
			# shifted = cv2.warpAffine(resized_im, M, (resized_im.shape[1], resized_im.shape[0]))
			# if rel_x is not None and rel_y is not None:
			# 	draw_pointer(rel_x + hor_shift, rel_y + ver_shift, shifted, scale=percent_scale/100, color=(0, 255, 0))
			# cv2.imshow(TITULO, shifted)
			# if is_mask:
			# 	apply_mask(True)

		elif event == cv2.EVENT_MOUSEMOVE:
			if panning:
				print('hor_shift_prev: ', hor_shift)
				print('ver_shift_prev: ', ver_shift)
				print('x: ', x)
				print('panning_x: ', panning_x)
				print('percent_scale: ', percent_scale)
				print('percent_scale / 100: ', percent_scale / 100)
				print('panning_x * (percent_scale / 100): ', panning_x * (percent_scale / 100))
				print('x - panning_x * (percent_scale / 100): ', x - panning_x * (percent_scale / 100))
				hor_shift += (x - panning_x) * (percent_scale / 100)
				ver_shift += (y - panning_y) * (percent_scale / 100)
				print('hor_shift_post: ', hor_shift)
				print('ver_shift_post: ', ver_shift)
				# Redraw the image with new shifts
				width = int(img.shape[1] * percent_scale / 100)
				height = int(img.shape[0] * percent_scale / 100)
				dim = (width, height)
				M = np.float32([
					[1, 0, hor_shift * percent_scale / 100],
					[0, 1, ver_shift * percent_scale / 100]
				])
				resized_im = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
				shifted = cv2.warpAffine(resized_im, M, (resized_im.shape[1], resized_im.shape[0]))
				if rel_x is not None and rel_y is not None:
					draw_pointer(rel_x + hor_shift, rel_y + ver_shift, shifted, scale=percent_scale/100, color=(0, 255, 0))
				cv2.imshow(TITULO, shifted)
				if is_mask:
					apply_mask(True)
			last_x = x
			last_y = y
		elif event == cv2.EVENT_RBUTTONUP:
			panning = False
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
			draw_pointer(rel_x + hor_shift, rel_y + ver_shift, shifted, scale=percent_scale/100, color=(0, 255, 0))
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
			# If rel_x and rel_y are provided, draw circle
			if rel_x is not None and rel_y is not None:
				draw_pointer(rel_x + hor_shift, rel_y + ver_shift, shifted, scale=percent_scale/100, color=(0, 255, 0))
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
	

	# displaying the image 
	# cv2.namedWindow(TITULO, cv2.WINDOW_NORMAL)
	blank_image = np.zeros((1, 1, 3), dtype=np.uint8)
	cv2.namedWindow('TEMP_WINDOW', cv2.WINDOW_NORMAL)

	# Display the blank image in the window
	cv2.imshow('TEMP_WINDOW', blank_image)
	cv2.setWindowProperty(
    'TEMP_WINDOW',
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
	)
	
	screen_width = cv2.getWindowImageRect('TEMP_WINDOW')[2]
	screen_height = cv2.getWindowImageRect('TEMP_WINDOW')[3]
 
	image_width =  img.shape[1]
	image_height =  img.shape[0]
	initial_scale = min(screen_width / image_width, screen_height / image_height)
	percent_scale = initial_scale * 100
 
	width = int(img.shape[1] * percent_scale / 100)
	height = int(img.shape[0] * percent_scale / 100)
	dim = (width, height)

	# resize image
	resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

	# If rel_x and rel_y are provided, draw pointer
	print('rel_x: ', rel_x)
	print('rel_y: ', rel_y)
	if rel_x is not None and rel_y is not None:
		draw_pointer(rel_x, rel_y, resized, scale=initial_scale, color=(0, 255, 0))
	
	cv2.destroyAllWindows() 
	cv2.imshow(TITULO, resized)
	
	window_width = cv2.getWindowImageRect(TITULO)[2]
	window_height = cv2.getWindowImageRect(TITULO)[3]

	# setting mouse handler for the image 
	# and calling the mouse_event() function 
	cv2.setMouseCallback(TITULO, mouse_event) 

	# wait for a key to be pressed to exit 
	key = -1

	while key != ord('s') and key != ord('S'):
		key = cv2.waitKey(33) & 0xFF  # Ensure proper event handling
		if cv2.getWindowProperty(TITULO, cv2.WND_PROP_VISIBLE) < 1:
			cv2.destroyAllWindows() 
			return None
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
		if (key == ord('m') or key == ord('M')) and (rel_x is None and rel_y is None):
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
					draw_pointer(rel_x + hor_shift, rel_y + ver_shift, shifted, scale=percent_scale/100, color=(0, 255, 0))
				cv2.imshow(TITULO, shifted)
				if is_mask:
					apply_mask(True)
	
 	# close the window 
	cv2.destroyAllWindows() 

	return coord