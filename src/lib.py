import os, sys
import tkinter, cv2, PIL.Image, PIL.ImageTk

def getFilenames(dir_name):
	filenames = os.listdir(dir_name)
	return filenames

def createFullScreenWindow():
	return 0

class App:
	def __init__(self, img_path, window, win_title='pi_display', win_bg='black',debug=True):
		# create a window and add a title to it
		self.window = window
		self.window.title(win_title)

		# set the backgournd color to black
		self.window.configure(background=win_bg)

		# make the window full screen and quit when pressing 'Esc'
		self.window.attributes('-fullscreen', True)
		self.window.bind('<Escape>',lambda e: self.window.destroy())
		self.win_w = self.window.winfo_width()
		self.win_h = self.window.winfo_height()
		if debug:
			print('win_w: %d\twin_h: %d\t' % (self.win_w, self.win_h))

		# load a image uisng OpenCV
		self.cv_img = cv2.imread(img_path)
		self.cv_img = cv2.cvtColor(self.cv_img, cv2.COLOR_BGR2RGB) # convet BGR to RGB
		self.img_h, self.img_w, self.img_c = self.cv_img.shape
		if debug:
			print('ori_img_w: %d\tori_img_h: %d\tori_img_c: %d' 
				% (self.img_w, self.img_h, self.img_c))

		# resize image to fit the window
		if self.img_w > self.win_w or self.img_h > self.win_h:
			self.ratio = min(self.win_w/self.img_w, self.win_h/self.img_h)
			self.img_w = int(self.img_w * self.ratio)
			self.img_h = int(self.img_h * self.ratio)
			self.cv_img = cv2.resize(self.cv_img, (self.img_w, self.img_h))
			if debug:
				print('ratio: %f\tnew_img_w: %d\tnew_img_h: %d' 
					% (self.ratio, self.img_w, self.img_h))

		# use Pillow to convert the Numpy ndarray to a PhotoImage
		self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cv_img))

		# create a canvas than can fit the above image
		self.canvas = tkinter.Canvas(self.window, 
			width=self.img_w, height=self.img_h, relief='flat', highlightthickness=0)
		self.canvas.pack()
		self.canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER) # center the canvas

		# add a PhotoImage to the canvas
		self.canvas.create_image(self.img_w/2, self.img_h/2, 
			image=self.photo, anchor=tkinter.CENTER) # center the image inside canvas



		# run the window loop
		self.window.mainloop()