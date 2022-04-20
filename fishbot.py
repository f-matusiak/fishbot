from PIL import ImageGrab
from threading import Thread
import pydirectinput
import time
import tkinter as tk
import win32gui

fishBotRunning = False
fishTime = 0

toplist, winlist = [], []

def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

win32gui.EnumWindows(enum_cb, toplist)

gromo = [(hwnd, title) for hwnd, title in winlist if 'gromo' in title.lower()]
# just grab the hwnd for first window matching gromo
gromo = gromo[0]
hwnd = gromo[0]


class FishBot(Thread):

    flag = True

    def __init__(self):
        super().__init__()

    def run(self):
        global fishBotRunning
        while fishBotRunning:
            
            img = self.getImg()
            img.show()
            color = img.getpixel((100, 100))
            print(color)
            if all(i >= 230 for i in color) and self.flag:
                self.flag = False
                global fishTime
                time.sleep(fishTime)
                self.pressSpace()

    def pressSpace(self):
        self.flag = True
        pydirectinput.keyDown('space')
        time.sleep(0.01)
        pydirectinput.keyUp('space')
        time.sleep(5)
        pydirectinput.keyDown('1')
        time.sleep(0.01)
        pydirectinput.keyUp('1')
        time.sleep(0.01)
        pydirectinput.keyDown('space')
        time.sleep(0.01)
        pydirectinput.keyUp('space')

    def getImg(self):
        global hwnd
        # nie wiem czemu sie crashuje kiedy probuje
        # dać okienko na gore
        # win32gui.SetForegroundWindow(hwnd)
        bbox = win32gui.GetWindowRect(hwnd)
        return ImageGrab.grab(bbox)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Fish bot tego typu')
        self.geometry('300x100')
        self.resizable(0, 0)

        self.StartButton = tk.Button(
            self, text="Start", command=self.startFishThread)
        self.StartButton.place(x=10, y=10)
        self.StopButton = tk.Button(
            self, text="Stop", command=self.stopFishThread)
        self.StopButton.place(x=60, y=10)
        self.TimeLabel = tk.Label(self, text="Time")
        self.TimeLabel.place(x=0, y=40)
        self.TimeEntry = tk.Entry(self)
        self.TimeEntry.place(x=50, y=40)
        self.TimeEntry.insert(0, '2')

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


if __name__ == "__main__":
    app = App()
    app.mainloop()
