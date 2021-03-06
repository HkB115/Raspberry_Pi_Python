#!/usr/bin/python
import os
import io
import datetime,time
sleep=time.sleep
try:
 import picamera
except:
 print("[ERROR] Install package python3-picamera")
 exit(0)
try:
 import wiringpi2 as wiringpi
except:
 try:
  import wiringpi
 except:
  wiringpi_installed=False
try:
 wiringpi.wiringPiSetup()
 wiringpi_installed=True
except:
 print("[WARN] WiringPi is required for LED functionality.")
from PIL import Image

##### Settings #####
delay=5 # Default: 5. Minimum delay between camera triggers in seconds
detect=True # Enable motion detection to run continuously
discrepancy_margin=25 # Default: 25. Allow for some differences. Useful if camera is pointed outside
led_array=True # Enable the LEDBorg module to activate when the camera takes a picture
led_color='red' # Default: 'red'. Choices: 'red', 'green', or 'blue'
trigger_threshold=2 # Default: 2. Minimum percent change in images to trigger the camera
####################

if(not(wiringpi_installed)):
 led_array=False
if(led_array):
 if(led_color=='red'):
  led_pin=0
 elif(led_color=='green'):
  led_pin=2
 elif(led_color=='blue'):
  led_pin=3
 else:
  led_pin=0
 wiringpi.pinMode(led_pin, wiringpi.GPIO.OUTPUT)
 pin=wiringpi.digitalWrite
 pin(0,0)
 pin(2,0)
 pin(3,0)
else:
 led_array=False

images=[]
while(detect):
 stream=io.BytesIO()
 with picamera.PiCamera() as comparator:
  comparator.resolution=(64,36)
  comparator.ISO=800
  comparator.capture(stream,format='jpeg')
 stream.seek(0)
 if(len(images)!=2):
  images.append(Image.open(stream))
 else:
  images[0]=Image.open(stream)
 discrepancies=0
 if(len(images)!=1):
  x=0
  while(x<images[0].size[0]):
   y=0
   while(y<images[0].size[1]):
    img0=images[0].getpixel((x,y))
    val0=img0[0]+img0[1]+img0[2]
    img1=images[1].getpixel((x,y))
    val1=img1[0]+img1[1]+img1[2]
    if(abs(val1-val0)>discrepancy_margin):
     discrepancies+=1
    y+=1
   x+=1
  trigger=(discrepancies*100)/(images[0].size[0]*images[0].size[1])
  #print(str(trigger)+"% changed.")
  if(trigger>=trigger_threshold):
   if(led_array==True):
    pin(led_pin,1)
   else:
    pin(led_pin,0)
   current_time=time.strftime("%y-%b-%dat%H:%M:%S",time.localtime())
   with picamera.PiCamera() as camera:
    camera.resolution=(1280,720)
    camera.brightness=50
    camera.ISO=800
    camera.capture("capture%s.jpg"%(current_time))
   pin(led_pin,0)
   #print("Camera triggered at %s"%(current_time))
  images[1]=images[0]
