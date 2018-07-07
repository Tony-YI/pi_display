import os, sys
import tkinter, cv2, PIL.Image, PIL.ImageTk

def getFilenames(dir_name):
	filenames = os.listdir(dir_name)
	return filenames

class App:
	def __init__(self, img_path, window, win_title='pi_display', win_bg='black', debug=True):
		# create a window for displaying images
		self.window, self.win_w, self.win_h = \
			self.createWindow(window, win_title, win_bg, debug)
		
		# load the image from img_path
		self.cv_img, self.img_w, self.img_h = \
			self.loadImg(img_path, debug)

		# resize the loaded image base on the window's size
		self.cv_img, self.img_w, self.img_h = \
			self.resizeImg(self.cv_img, self.img_w, self.img_h, self.win_w, self.win_h, debug)

		# convert the loaded imaged to format that Tkinter used
		self.photo = \
			self.convertCVImgToPILImage(self.cv_img, debug)

		# create a canvas to display the converted image
		self.canvas = \
			self.createCanvas(self.window, self.photo, self.img_w, self.img_h, debug)

		tkinter.Button(window, text='Capture', commnad=changeImgOnKey)

		# run the window loop
		self.window.mainloop()

	def createWindow(self, window, win_title, win_bg, debug):
		# create a window and add a title to it
		window.title(win_title)

		# set the backgournd color to black
		window.configure(background=win_bg)

		# make the window full screen and quit when pressing 'Esc'
		window.attributes('-fullscreen', True)
		window.bind('<Escape>',lambda e: window.destroy())
		win_w = window.winfo_screenwidth()
		win_h = window.winfo_screenheight()
		if debug:
			print('win_w: %d\twin_h: %d\t' % (win_w, win_h))
		return window, win_w, win_h

	def loadImg(self, img_path, debug):
		# load a image uisng OpenCV
		cv_img = cv2.imread(img_path)
		cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB) # convet BGR to RGB
		img_h, img_w, img_c = cv_img.shape
		if debug:
			print('ori_img_w: %d\tori_img_h: %d\tori_img_c: %d' 
				% (img_w, img_h, img_c))
		return cv_img, img_w, img_h

	def resizeImg(self, cv_img, img_w, img_h, win_w, win_h, debug):
		# resize image to fit the window
		if img_w > win_w or img_h > win_h:
			ratio = min(win_w/img_w, win_h/img_h)
			img_w = int(img_w * ratio)
			img_h = int(img_h * ratio)
			cv_img = cv2.resize(cv_img, (img_w, img_h))
			if debug:
				print('ratio: %f\tnew_img_w: %d\tnew_img_h: %d' 
					% (ratio, img_w, img_h))
		return cv_img, img_w, img_h

	def convertCVImgToPILImage(self, cv_img, debug):
		# use Pillow to convert the Numpy ndarray to a PhotoImage
		photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv_img))
		return photo

	def createCanvas(self, window, photo, img_w, img_h, debug):
		# create a canvas than can fit the above image
		canvas = tkinter.Canvas(window, 
			width=img_w, height=img_h, relief='flat', highlightthickness=0)
		canvas.pack()
		canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER) # center the canvas

		# add a PhotoImage to the canvas
		canvas.create_image(img_w/2, img_h/2, 
			image=photo, anchor=tkinter.CENTER) # center the image inside canvas
		return canvas

	def changeImgOnKey():
		printf('changeImgOnKey()')