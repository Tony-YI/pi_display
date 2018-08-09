import os, sys, imghdr, imageio
import tkinter, cv2, PIL.Image, PIL.ImageTk
import numpy as np

def getFilenames(dir_name):
	file_names = os.listdir(dir_name)
	return file_names

class App:
	def __init__(self, img_dir, update_effect='update', update_condic='onKey', debug=True):
		# remove the .DS_Store if exist
		file_names = getFilenames(img_dir)
		if '.DS_Store' in file_names:
			os.remove(img_dir + '.DS_Store')

		# define some options here
		self.update_img_effects = {'update', 'fadeOutAndIn', 'fadeOutThenIn'}
		self.update_condictions = {'onKey', 'timeOut'}
		self.img_types 			= {'img', 'gif'}
		self.win_title 			= 'pi_display'
		self.win_bg 			= 'black'

		# flag used to determine printing debug information or not
		self.debug = debug
		img_names = getFilenames(img_dir)
		self.img_paths = [img_dir + img_name for img_name in img_names]
		if self.debug:
			print(img_names)

		# create a window for displaying images
		self.window, self.win_w, self.win_h = \
			self.createWindow(self.win_title, self.win_bg)

		# create a black image with win_w x win_h for future usage
		self.cur_img_type = 'img'
		self.pre_img_type = self.cur_img_type
		self.bg_cv_img = np.zeros((self.win_h, self.win_w, 3), np.uint8)

		# create a canvas to display the background image
		self.cur_cv_img = self.bg_cv_img.copy()
		self.pre_cv_img = self.cur_cv_img.copy()
		self.photo = self.convertCVImgToPILImage(self.cur_cv_img, self.cur_img_type)
		self.cur_img_h, self.cur_img_w, self.cur_img_c = self.cur_cv_img.shape
		self.pre_img_h, self.pre_img_w, self.pre_img_c = self.pre_cv_img.shape

		self.photo_on_canvas, self.canvas = \
			self.createCanvas(self.window, self.photo, self.cur_img_w, self.cur_img_h)

		# select a effect for switching images
		self.update_effect = update_effect
		self.update_condic = update_condic

		# get the index of images in img_dir
		self.img_path_ind = 0
		self.img_path_len = len(self.img_paths)

		# display images
		self.display()

		# run the window loop
		self.window.mainloop()

	def createWindow(self, win_title, win_bg):
		# create a window and add a title to it
		window = tkinter.Tk()
		window.title(win_title)

		# set the backgournd color to black
		window.configure(background=win_bg)

		# make the window full screen and quit when pressing 'Esc'
		window.attributes('-fullscreen', True)
		window.bind('<Escape>', lambda e: window.destroy())
		win_w = window.winfo_screenwidth()
		win_h = window.winfo_screenheight()
		if self.debug:
			print('win_w: %d\twin_h: %d\t' % (win_w, win_h))
		return window, win_w, win_h

	def cpoyCurImgToPreImg(self):
		self.pre_cv_img 	= self.cur_cv_img.copy()
		self.pre_img_type 	= self.cur_img_type
		self.pre_img_w		= self.cur_img_w
		self.pre_img_h		= self.cur_img_h
		self.pre_img_c		= self.cur_img_c

	def loadImg(self, img_path):
		file_type = imghdr.what(img_path)

		if file_type == 'gif':
			img_type = 'gif'
			# load a image uisng imageio
			cv_img = imageio.mimread(img_path)
			img_h, img_w, img_c = cv_img[0].shape
			if self.debug:
				print('ori_img_w: %d\tori_img_h: %d\tori_img_c: %d' 
					% (img_w, img_h, img_c))
			return cv_img, img_w, img_h, img_type

		elif file_type == 'png' or file_type == 'jpeg':
			img_type = 'img'
			# load a image uisng OpenCV
			cv_img = cv2.imread(img_path)
			cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB) # convet BGR to RGB
			img_h, img_w, img_c = cv_img.shape
			if self.debug:
				print('ori_img_w: %d\tori_img_h: %d\tori_img_c: %d' 
					% (img_w, img_h, img_c))
			return cv_img, img_w, img_h, img_type
		else:
			printf('Errot: loadImg() => invalid file type %s' % file_type)
			sys.exit()

	def resizeImg(self, cv_img, img_w, img_h, win_w, win_h, img_type):
		# resize image to fit the window
		if (img_w > win_w or img_h > win_h) or (img_w < win_w and img_h < win_h):
			ratio = min(win_w/img_w, win_h/img_h)
			img_w = int(img_w * ratio)
			img_h = int(img_h * ratio)
			if img_type == 'img':
				cv_img = cv2.resize(cv_img, (img_w, img_h))
			elif img_type == 'gif':
				cv_img = [cv2.resize(img, (img_w, img_h)) for img in cv_img]
			if self.debug:
				print('ratio: %f\tnew_img_w: %d\tnew_img_h: %d' 
					% (ratio, img_w, img_h))

		delta_w = win_w - img_w
		delta_h = win_h - img_h
		top, bottom = delta_h // 2, delta_h - (delta_h // 2)
		left, right = delta_w // 2, delta_w - (delta_w // 2)
		if img_type == 'img':
			cv_img = cv2.copyMakeBorder(cv_img, top, bottom, left, right, cv2.BORDER_CONSTANT,
				value=[0,0,0]) # black
			img_h, img_w, img_c = cv_img.shape
			return cv_img, img_w, img_h
		elif img_type == 'gif':
			cv_img = [cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
				value=[0,0,0]) for img in cv_img] # black
			img_h, img_w, img_c = cv_img[0].shape
			return cv_img, img_w, img_h

	def convertCVImgToPILImage(self, cv_img, img_type):
		# use Pillow to convert the Numpy ndarray to a PhotoImage
		if img_type == 'img':
			photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv_img))
			return photo
		elif img_type == 'gif':
			photo = [PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img)) for img in cv_img]
			return photo

	def createCanvas(self, window, photo, img_w, img_h):
		canvas = tkinter.Canvas(window, 
			width=img_w, height=img_h, relief='flat', bg=self.win_bg, highlightthickness=0)
		canvas.pack()
		canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER) # center the canvas

		# add a PhotoImage to the canvas
		photo_on_canvas = canvas.create_image(img_w/2, img_h/2, 
			image=photo, anchor=tkinter.CENTER) # center the image inside canvas
		return photo_on_canvas, canvas

	def effectFadeOutAndIn(self, pre_cv_img, pre_img_type, cur_cv_img, cur_img_type, alpha=100):
		next_alpha = alpha - 10
		if next_alpha >= 0:
			temp_cv_img = cv2.addWeighted(pre_cv_img, next_alpha/100.0, cur_cv_img, (100-next_alpha)/100.0, 0)
			self.photo = self.convertCVImgToPILImage(temp_cv_img, 'img')
			self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)
			self.canvas.update()	
			self.canvas.after(10, self.effectFadeOutAndIn, 
				pre_cv_img, pre_img_type, cur_cv_img, pre_img_type, next_alpha)
		else:
			if self.update_condic == 'onKey':
				self.window.bind('<Key>', self.callbackChangeImgOnKey) # re-bind <key>
			elif self.update_condic == 'timeOut':
				self.window.after(5000, self.callbackChangeImgTimeOut)

	def effectFadeOutThenIn(self, pre_cv_img, pre_img_type, cur_cv_img, cur_img_type, alpha=100):
		next_alpha = alpha - 10
		if next_alpha >= 0:
			temp_cv_img = cv2.addWeighted(pre_cv_img, next_alpha/100.0,
				self.bg_cv_img, (100-next_alpha)/100.0, 0)
			self.photo = self.convertCVImgToPILImage(temp_cv_img, 'img')
			self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)
			self.canvas.update()			
			self.canvas.after(10, self.effectFadeOutThenIn,
				pre_cv_img, pre_img_type, cur_cv_img, cur_img_type, next_alpha)
		elif next_alpha < 0 and next_alpha >= -100:
			temp_cv_img = cv2.addWeighted(cur_cv_img, abs(next_alpha/100.0), 
				self.bg_cv_img, (1-abs(next_alpha))/100.0, 0)
			self.photo = self.convertCVImgToPILImage(temp_cv_img, 'img')
			self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)
			self.canvas.update()			
			self.canvas.after(10, self.effectFadeOutThenIn,
				pre_cv_img, pre_img_type, cur_cv_img, cur_img_type, next_alpha)
		else:
			if self.update_condic == 'onKey':
				self.window.bind('<Key>', self.callbackChangeImgOnKey) # re-bind <key>
			elif self.update_condic == 'timeOut':
				self.window.after(5000, self.callbackChangeImgTimeOut)

	def effectUpdate(self, cv_img, img_type):
		self.photo = self.convertCVImgToPILImage(cv_img, img_type)
		if img_type == 'img':
			self.displayImg()
		elif img_type == 'gif':
			self.displayGif()

		if self.update_condic == 'onKey':
			self.window.bind('<Key>', self.callbackChangeImgOnKey) # re-bind <key>
		elif self.update_condic == 'timeOut':
			self.window.after(5000, self.callbackChangeImgTimeOut)

	def callbackChangeImgOnKey(self, event):
		# un-bind <key>
		self.window.unbind('<Key>')

		update_img_flag = False
		if event.keysym == 'Left':
			if self.img_path_ind == 0:
				self.img_path_ind = self.img_path_len - 1
			else:
				self.img_path_ind = self.img_path_ind - 1
			update_img_flag = True

		elif event.keysym == 'Right':
			if self.img_path_ind == self.img_path_len - 1:
				self.img_path_ind = 0
			else:
				self.img_path_ind = self.img_path_ind + 1
			update_img_flag = True

		if update_img_flag:
			self.cpoyCurImgToPreImg()
			self.cur_cv_img, self.cur_img_w, self.cur_img_h, self.cur_img_type = \
				self.loadImg(self.img_paths[self.img_path_ind])
			self.cur_cv_img, self.cur_img_w, self.cur_img_h = \
				self.resizeImg(self.cur_cv_img, self.cur_img_w, self.cur_img_h,
					self.win_w, self.win_h, self.cur_img_type)

			if self.update_effect == 'update':
				self.effectUpdate(self.cur_cv_img, self.cur_img_type)
			elif self.update_effect == 'fadeOutAndIn':
				self.effectFadeOutAndIn(self.pre_cv_img, self.pre_img_type, self.cur_cv_img, self.cur_img_type)
			elif self.update_effect == 'fadeOutThenIn':
				self.effectFadeOutThenIn(self.pre_cv_img, self.pre_img_type, self.cur_cv_img, self.cur_img_type)

		if self.debug:
			print('changeImgOnKey() event: %s' % event.keysym)

	def callbackChangeImgTimeOut(self):
		if self.img_path_ind == self.img_path_len - 1:
			self.img_path_ind = 0
		else:
			self.img_path_ind = self.img_path_ind + 1

		self.cpoyCurImgToPreImg()
		self.cur_cv_img, self.cur_img_w, self.cur_img_h, self.cur_img_type = \
			self.loadImg(self.img_paths[self.img_path_ind])
		self.cur_cv_img, self.cur_img_w, self.cur_img_h = \
			self.resizeImg(self.cur_cv_img, self.cur_img_w, self.cur_img_h,
				self.win_w, self.win_h, self.cur_img_type)

		if self.update_effect == 'update':
			self.effectUpdate(self.cur_cv_img, self.cur_img_type)
		elif self.update_effect == 'fadeOutAndIn':
			self.effectFadeOutAndIn(self.pre_cv_img, self.pre_img_type, self.cur_cv_img, self.cur_img_type)
		elif self.update_effect == 'fadeOutThenIn':
			self.effectFadeOutThenIn(self.pre_cv_img, self.pre_img_type, self.cur_cv_img, self.cur_img_type)

	def setUpdateEffect(self, update_effect):
		if update_effect not in self.update_img_effects:
			print('Warning: setUpdateEffect() => No such update_effect: %s, change to default.'
				% self.update_effect)
			self.update_effect = 'update'

	def setUpdateCondiction(self, update_condic):
		if update_condic == 'onKey':
			self.window.bind('<Key>', self.callbackChangeImgOnKey)
		elif update_condic == 'timeOut':
			self.window.after(5000, self.callbackChangeImgTimeOut)
		else:
			print('Warning: setUpdateCondiction() => No such update_condic: %s, change to default.'
				% update_condic)
			self.window.bind('<Key>', self.callbackChangeImgOnKey)

	def displayImg(self):
		self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)
		self.canvas.update()

	def displayGif(self, frame=0):
		print('current frame: %d' % frame)
		next_frame = 0
		if frame + 1 < len(self.photo):
			next_frame = frame + 1
		else:
			next_frame = 0
		self.canvas.itemconfig(self.photo_on_canvas, image=self.photo[frame])
		self.canvas.update()
		self.canvas.after(15, self.displayGif, next_frame)

	def display(self):
		self.cpoyCurImgToPreImg()
		self.cur_cv_img, self.cur_img_w, self.cur_img_h, self.cur_img_type = \
			self.loadImg(self.img_paths[0])
		self.cur_cv_img, self.cur_img_w, self.cur_img_h = \
			self.resizeImg(self.cur_cv_img, self.cur_img_w, self.cur_img_h,
				self.win_w, self.win_h, self.cur_img_type)
		self.photo = \
			self.convertCVImgToPILImage(self.cur_cv_img, self.cur_img_type)

		if self.cur_img_type == 'img':
			self.displayImg()
		elif self.cur_img_type == 'gif':
			self.displayGif()

		self.setUpdateEffect(self.update_effect)
		self.setUpdateCondiction(self.update_condic)