import os, sys
import tkinter, cv2, PIL.Image, PIL.ImageTk

def getFilenames(dir_name):
	filenames = os.listdir(dir_name)
	return filenames

def createFullScreenWindow():
	return 0

def test():
	# create a window
	window = tkinter.Tk()

	# add title to the window
	window.title('pi_display')

	# make the window full screen and quit when pressing 'Esc'
	window.attributes('-fullscreen', True)
	window.bind('<Escape>',lambda e: window.destroy())

	# load a image uisng OpenCV
	cv_img = cv2.imread('../img/angry_cat.jpg')
	img_h, img_w, img_c = cv_img.shape
	print('img_h: %d\timg_w: %d\timg_c: %d\t' % (img_h, img_w, img_c))

	# create a canvas than can fit the above image
	canvas = tkinter.Canvas(window, width=img_w, height=img_h)
	canvas.pack()

	# use Pillow to convert the Numpy ndarray to a PhotoImage
	photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv_img))

	# add a PhotoImage to the canvas
	canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)

	# run the window loop
	window.mainloop()