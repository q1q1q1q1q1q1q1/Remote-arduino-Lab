import threading

import cv2
import serial
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
import random
import os
from .models import File
from getAllSerialPorts import getPorts

start = True
output = []
typicalBaudrate = 9600  # for arduino uno 115200
cam = None


def ajax(request):

    return JsonResponse({"out": output})

def index(request):
    global start
    global output
    if request.method == "POST":
        if len(request.FILES) != 0:
            if str(request.FILES["document"]).split(".")[-1] == "hex":
                #         <--- here getting number arduino --->
                start = False
                flashArduino(request)
                req = File()
                req.title = request.FILES["document"]
                req.file = request.FILES["document"]
                req.save()
                start = True
                output.clear()

    return render(request, "loadhex/index.html")


def flashArduino(request):
    hex_file = request.FILES["document"]
    fs = FileSystemStorage()
    genName = str(int(random.random() * 100)) + "_" + hex_file.name
    fs.save(genName, hex_file)
    path = "/home/pi/remotelyAdrduino/media/" + genName
    os.system(f"avrdude -v -patmega328p -carduino -P {getArduinoPort()} -b115200 -D -Uflash:w:{path}:i")


def video_feed(request):
    global cam
    if cam is None:
        cam = VideoCamera()
    return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.grabbed, self.frame = self.video.read()
        threading.Thread(target=self.update, args=()).start()
        threading.Thread(target=self.update, args=()).start()
        threading.Thread(target=readS, args=()).start()

    def __del__(self):
        self.video.release()

    def getFrame(self):
        image = self.frame

        _, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tobytes()

    def update(self):
        while True:
            self.grabbed, self.frame = self.video.read()


def gen(camera):
    while True:
        frame = camera.getFrame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def readS():
    global start
    global output
    ser = serial.Serial(port=getArduinoPort(),
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout=0)
    seq = []
    while True:
        if start is True:
            if ser.is_open is False:
                ser.open()

            for c in ser.read():
                seq.append(chr(c))
                joined_seq = ''.join(str(v) for v in seq)
                if chr(c) == '\n':
                    exist = False
                    for str_ in output:
                        if  str_ == joined_seq:
                            exist = True
                    if not exist:
                         output.append(joined_seq)
                    seq = []
                    break
        else:
            ser.close()


def getArduinoPort():
    ports = getPorts()
    invalidPorts = ["/dev/tty.Bluetooth-Incoming-Port", "/dev/ttyAMA0"]
    for port in ports:
        validPort = True
        for invalidP in invalidPorts:
            if port == invalidP:
                validPort = False
            else: continue
        if validPort is True:
            return port
    return None
