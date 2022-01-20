#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep

cam = PiCamera()

cam.resolution = (1024, 768)
cam.start_preview()
sleep(2)
cam.capture('foo.jpg')

cam.close()
