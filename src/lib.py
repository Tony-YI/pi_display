import os, sys
import tkinter

def getFilenames(dir_name):
	filenames = os.listdir(dir_name)
	return filenames

def createFullScreenWindow():
	return 0