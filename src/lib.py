import os, sys
import tkinter, cv2, PIL.Image, PIL.ImageTk

def getFilenames(dir_name):
	file_names = os.listdir(dir_name)
	return file_names

class App:
	def __init__(self, img_dir, window, win_title='pi_display', win_bg='black', debug=True):
		# remove the .DS_Store if exist
		file_names = getFilenames(img_dir)
		if '.DS_Store' in file_names:
			os.remove(img_dir + '.DS_Store')

		# flag used to determine printing debug information or not
		self.win_bg = win_bg
		self.debug = debug
		img_names = getFilenames(img_dir)
		self.img_paths = [img_dir + img_name for img_name in img_names]
		if self.debug:
			print(img_names)

		# create a window for displaying images
		self.window, self.win_w, self.win_h = \
			self.createWindow(window, win_title, win_bg)
		
		# load the first image from img_paths
		self.cv_img, self.img_w, self.img_h = \
			self.loadImg(self.img_paths[0])
		self.img_path_ind = 0
		self.img_path_len = len(self.img_paths)

		# resize the loaded image base on the window's size
		self.cv_img, self.img_w, self.img_h = \
			self.resizeImg(self.cv_img, self.img_w, self.img_h, self.win_w, self.win_h)

		# convert the loaded imaged to format that Tkinter used
		self.photo = \
			self.convertCVImgToPILImage(self.cv_img)

		# create a canvas to display the converted image
		self.photo_on_canvas, self.canvas = \
			self.createCanvas(self.window, self.photo, self.img_w, self.img_h)

		self.window.bind('<Key>', self.callbackChangeImgOnKey)

		# run the window loop
		self.window.mainloop()

	def createWindow(self, window, win_title, win_bg):
		# create a window and add a title to it
		window.title(win_title)

		# set the backgournd color to black
		window.configure(background=win_bg)

		# make the window full screen and quit when pressing 'Esc'
		window.attributes('-fullscreen', True)
		window.bind('<Escape>',lambda e: window.destroy())
		win_w = window.winfo_screenwidth()
		win_h = window.winfo_screenheight()
		if self.debug:
			print('win_w: %d\twin_h: %d\t' % (win_w, win_h))
		return window, win_w, win_h

	def loadImg(self, img_path):
		# load a image uisng OpenCV
		cv_img = cv2.imread(img_path)
		cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB) # convet BGR to RGB
		img_h, img_w, img_c = cv_img.shape
		if self.debug:
			print('ori_img_w: %d\tori_img_h: %d\tori_img_c: %d' 
				% (img_w, img_h, img_c))
		return cv_img, img_w, img_h

	def resizeImg(self, cv_img, img_w, img_h, win_w, win_h):
		# resize image to fit the window
		if img_w > win_w or img_h > win_h:
			ratio = min(win_w/img_w, win_h/img_h)
			img_w = int(img_w * ratio)
			img_h = int(img_h * ratio)
			cv_img = cv2.resize(cv_img, (img_w, img_h))
			if self.debug:
				print('ratio: %f\tnew_img_w: %d\tnew_img_h: %d' 
					% (ratio, img_w, img_h))
		return cv_img, img_w, img_h

	def convertCVImgToPILImage(self, cv_img):
		# use Pillow to convert the Numpy ndarray to a PhotoImage
		photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv_img))
		return photo

	def createCanvas(self, window, photo, img_w, img_h):
		# create a canvas than can fit the above image
		canvas = tkinter.Canvas(window, 
			width=img_w, height=img_h, relief='flat', bg=self.win_bg, highlightthickness=0)
		canvas.pack()
		canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER) # center the canvas

		# add a PhotoImage to the canvas
		photo_on_canvas = canvas.create_image(img_w/2, img_h/2, 
			image=photo, anchor=tkinter.CENTER) # center the image inside canvas
		return photo_on_canvas, canvas

	def updateCanvas(self, img_path):
		self.cv_img, self.img_w, self.img_h = \
			self.loadImg(img_path)
		self.cv_img, self.img_w, self.img_h = \
			self.resizeImg(self.cv_img, self.img_w, self.img_h, self.win_w, self.win_h)
		self.photo = \
			self.convertCVImgToPILImage(self.cv_img)
		# reconfigure canvas size and the image on it
		self.canvas.configure(width=self.img_w, height=self.img_h)
		self.canvas.itemconfig(self.photo_on_canvas, image=self.photo)
		self.canvas.coords(self.photo_on_canvas, self.img_w/2, self.img_h/2)

	def callbackChangeImgOnKey(self, event):
		event = event.getattr()
		if event.keysym == 'Left':
			print('Left')
			if self.img_path_ind == 0:
				self.img_path_ind = self.img_path_len - 1
			else:
				self.img_path_ind = self.img_path_ind - 1
			self.updateCanvas(img_path=self.img_paths[self.img_path_ind])

		elif event.keysym == 'Right':
			print('Right')
			if self.img_path_ind == self.img_path_len - 1:
				self.img_path_ind = 0
			else:
				self.img_path_ind = self.img_path_ind + 1
			self.updateCanvas(img_path=self.img_paths[self.img_path_ind])

		if self.debug:
			print('changeImgOnKey() event: %s' % event)