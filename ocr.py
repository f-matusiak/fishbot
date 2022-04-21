from PIL import ImageGrab
from threading import Thread
from datetime import datetime
import pydirectinput
import time
import tkinter as tk
import win32gui
import cv2
import numpy as np
import pytesseract

fishBotRunning = False
fishTime = 2800
captureRunning = False

toplist, winlist = [], []

def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

win32gui.EnumWindows(enum_cb, toplist)

gromo = [(hwnd, title) for hwnd, title in winlist if 'gromo' in title.lower()]
# just grab the hwnd for first window matching gromo
gromo = gromo[0]
hwnd = gromo[0]

class GameCapture(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        global gameScreen, hwnd, captureRunning
        while captureRunning:
            # nie wiem czemu sie crashuje kiedy probuje
            # dać okienko na gore
            # win32gui.SetForegroundWindow(hwnd)
            bbox = win32gui.GetWindowRect(hwnd)
            gameScreen = ImageGrab.grab(bbox)
            # jezeli 7% uzycia procesora to za duzo
            # to taki timeout zmniejsza uzycie do 1%
            # time.sleep(0.1)

class FishBot(Thread):

    flag = True
    counter = 0

    def __init__(self):
        super().__init__()

    def run(self):
        global fishBotRunning, captureRunning, gameScreen, fishTime
        if (not captureRunning):
            print('Start Capture first!')
            return
        print('FishTime: ', fishTime)
        while fishBotRunning:
            emote = gameScreen.copy().crop((550, 50, 600, 100))
            emoteColor = emote.getpixel((15, 15))
            if all(i >= 230 for i in emoteColor) and self.flag:
                start = time.time()
                text = self.getChat(gameScreen)
                self.flag = False
                # sprawdz jaki ma byc timeout
                time.sleep((fishTime / 1000) - (time.time() - start))
                self.pressSpace()
                print(text)

    def pressSpace(self):
        self.flag = True
        self.counter += 1
        pydirectinput.keyDown('space')
        time.sleep(0.01)
        pydirectinput.keyUp('space')
        time.sleep(4.5)
        pydirectinput.keyDown('1')
        time.sleep(0.01)
        pydirectinput.keyUp('1')
        time.sleep(0.01)
        pydirectinput.keyDown('space')
        time.sleep(0.01)
        pydirectinput.keyUp('space')

    def getChat(self, gameScreen):

        chat = gameScreen.crop((15, 750, 420, 764))
        matrix = cv2.cvtColor(np.array(chat), cv2.COLOR_RGB2BGR)
        img = cv2.cvtColor(matrix, cv2.COLOR_BGR2GRAY)
        _, th1 = cv2.threshold(img,164,255,cv2.THRESH_BINARY)

        tes_config = r'--oem 3 --psm 6'

        return pytesseract.image_to_string(th1, config=tes_config, lang='eng+pol')

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Fish bot tego typu')
        self.geometry('300x100')
        self.resizable(0, 0)

        self.StartCaptureButton = tk.Button(
            self, text="Start Capture", command=self.startCaptureThread)
        self.StartCaptureButton.place(x=10, y=10)
        self.StopCaptureButton = tk.Button(
            self, text="Stop Capture", command=self.stopCaptureThread)
        self.StopCaptureButton.place(x=95, y=10)

        self.StartFishButton = tk.Button(
            self, text="Start Fish", command=self.startFishThread)
        self.StartFishButton.place(x=10, y=40)
        self.StopFishButton = tk.Button(
            self, text="Stop Fish", command=self.stopFishThread)
        self.StopFishButton.place(x=75, y=40)


        self.TimeLabel = tk.Label(self, text="Time:")
        self.TimeLabel.place(x=10, y=70)
        self.TimeEntry = tk.Entry(self)
        self.TimeEntry.place(x=50, y=70)
        self.TimeEntry.insert(0, '2800')

    def startFishThread(self):
        global fishBotRunning
        global fishTime
        fishBotRunning = True
        fishTime = int(self.TimeEntry.get())
        fishbot_thread = FishBot()
        fishbot_thread.start()

    def stopFishThread(self):
        global fishBotRunning
        fishBotRunning = False

    def startCaptureThread(self):
        global captureRunning
        captureRunning = True
        capture_thread = GameCapture()
        capture_thread.start()

    def stopCaptureThread(self):
        global captureRunning
        captureRunning = False


if __name__ == "__main__":
    app = App()
    app.mainloop()
