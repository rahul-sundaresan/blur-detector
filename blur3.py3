# python script to extract frames from video and check if its blurry
from imutils import paths
import argparse
import cv2
import csv
import time
#!/usr/bin/python3

import os #to get file creation time
import math
import datetime

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
    help="path to save the grabbed images")
ap.add_argument("-t", "--threshold", type=float, default=100.0,
    help="focus measures that fall below this value will be considered 'blurry'")
ap.add_argument("-o", "--output", required=True,
    help="Specifies the CSV file for the output to be written to")
ap.add_argument("-v", "--video_input", required=True,
	help="Specifies the input video")
ap.add_argument("-c", "--capture_interval", type=int, default=1,
	help="Specifies the interval at which a frame must be captured (in seconds). Default is 1")
args = vars(ap.parse_args())


videoFile = args["video_input"]
imagesFolder = args["images"]
outputCSV = open(args["output"], 'w', newline='')#new line parameter to prevent extra new lines https://stackoverflow.com/a/3348664
interval = args["capture_interval"]

start = time.time()
#extracting frames
cap = cv2.VideoCapture(videoFile)
frameRate = cap.get(5) #frame rate
totalFrameDigit = len(str(cap.get(7))) #number of digits of total number of frames. We'll use this for formatting the output later
while(cap.isOpened()):
    frameId = cap.get(1) #current frame number
    ret, frame = cap.read()
    if (ret != True):
        break
    if (frameId % (math.floor(frameRate)*interval) == 0):
        filename = imagesFolder + "/image_" +  str(int(frameId)).zfill(totalFrameDigit) + ".jpg" 
        #^^^^ Images get saved as IMG 0001, IMG 0023, IMG 0300. Used for listing alphabetically when processing
        cv2.imwrite(filename, frame)
cap.release()
end = time.time() - start
print("Done extracting frames!")
print("Elapsed time :{} secs.".format(str(end)[:7]))


writtenData=[] #array to hold the data we'll write to the csv

vidcap = cv2.VideoCapture(args["video_input"])


# loop over the input images
for PathToImage in paths.list_images(args["images"]):
    ColorImage = cv2.imread(PathToImage)
    GreyScaleImage = cv2.cvtColor(ColorImage, cv2.COLOR_BGR2GRAY)
    VarianceOfLaplacian = cv2.Laplacian(GreyScaleImage, cv2.CV_64F).var()
    isBlurry = "not blurry"
 
    # if the focus measure is less than the supplied threshold,
    # then the image should be considered "blurry"
    if VarianceOfLaplacian < args["threshold"]:
        isBlurry = "blurry"
    rowData=[]
    rowData.extend([os.path.abspath(PathToImage),isBlurry,VarianceOfLaplacian,os.path.getctime(PathToImage),datetime.datetime.fromtimestamp(
        int(os.path.getctime(PathToImage))
    ).strftime('%Y-%m-%d %H:%M:%S')
	])
    writtenData.append(rowData)

with outputCSV:
    writer = csv.writer(outputCSV)
    writer.writerows(writtenData)
     
print("Writing complete")
