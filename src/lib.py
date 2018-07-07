import os, sys
import tkinter, cv2, PIL.Image, PIL.ImageTk

def getFilenames(dir_name):
	filenames = os.listdir(dir_name)
	return filenames

def createFullScreenWindow():
	return 0