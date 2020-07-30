from PIL import Image, ImageTk
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from datetime import datetime
import cv2
import os
import numpy

script_dir = os.path.dirname(__file__)


class App:
    def __init__(self, window=None):
        self.window = window
        self.cap = None
        self.current_image = None
        # Status
        self.playing = False
        self.isVideo = False
        self.totalFrame = 0
        self.frameCount = 0
        self.fps = 1
        self.frameInterval = 10
        self.rate = 1
        # Video Panel
        self.videoPanel = tk.Label(self.window, text="\/ Check Here to start!                ")
        self.videoPanel.pack(fill="both", expand=True, padx=10, pady=10)
        # Control Panel
        self.controlPanel = tk.Frame(self.window)
        tk.Button(self.controlPanel, text="Use Camera", command=lambda: self.useCamera()).pack(
            side=tk.LEFT, padx=(100, 0)
        )
        tk.Button(self.controlPanel, text="Open File", command=lambda: self.handleOpen()).pack(side=tk.LEFT)
        tk.Button(self.controlPanel, text="Take a Picture", command=lambda: self.screenShot()).pack(side=tk.LEFT)
        tk.Button(self.controlPanel, text="Play / Pause", command=lambda: self.playPause()).pack(side=tk.LEFT)
        tk.Button(self.controlPanel, text="<<", command=lambda: self.setRate(+0.2)).pack(side=tk.LEFT)
        tk.Button(self.controlPanel, text=">>", command=lambda: self.setRate(-0.2)).pack(side=tk.LEFT)
        self.frameLabel = tk.Label(self.controlPanel, text="", width=20)
        self.frameLabel.pack(side=tk.LEFT)
        self.controlPanel.pack()
        self.frameLoop()

    def useCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.frameCount = 0
        self.totalFrame = -1
        self.isVideo = False
        self.frameInterval = 10
        self.rate = 1
        self.frameLabel.configure(text="")
        self.playing = True
        print("\n==========Camera=========")
        print("Camera ID: 0")
        print("Frames Wait Time:", self.frameInterval)
        print("=========================\n")

    def handleOpen(self):
        path = tk.filedialog.askopenfilename()
        if path:
            if path.split(".")[-1].lower() in ["mkv", "mp4", "avi", "mov", "mpeg", "flv", "wmv"]:
                self.openFile(path)
            else:
                tk.messagebox.showinfo("無法開啟檔案","此檔案不是支援的影片檔")

    def openFile(self, path):
        self.cap = cv2.VideoCapture(path)
        self.frameCount = 0
        self.getDetails()
        self.isVideo = True
        self.playing = True
        print("\n==========Video==========")
        print("File:", path)
        print("File Type:", path.split(".")[-1])
        print("FPS:", self.fps)
        print("Total Frames:", self.totalFrame)
        print(f"Frame Interval: {self.frameInterval}ms")
        print("=========================\n")

    def getDetails(self):
        self.totalFrame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frameInterval = int(500 / self.fps)
        self.rate = 1

    def playPause(self):
        if not self.cap:
            return
        if self.playing:
            self.playing = False
            return
        self.playing = True

    def setRate(self, val):
        if not self.isVideo or not self.playing:
            return
        if self.rate <= 0.3 and val == -0.2:
            return
        if self.rate >= 4 and val == +0.2:
            return
        self.rate += val
        print("\n=======Rate Change=======")
        print(f"Current Rate: {self.rate} (0.2~4.0)")
        print(f"Frame Interval: {int(self.frameInterval * self.rate)}ms")
        print("=========================\n")

    def frameLoop(self):
        if self.playing:
            self.cap.grab()
            self.frameCount += 1
            # skip 1 frame for better performance
            if self.frameCount % 2 == 0:
                if self.isVideo:
                    self.frameLabel.configure(
                        text=f"{self.frameCount}/{self.totalFrame} - {round((self.frameCount / self.totalFrame)*100, 2)}%"
                    )
                ok, self.current_image = self.cap.retrieve()
                if ok:
                    resizedFrame = cv2.resize(self.current_image, (1280, 720))
                    cv2image = cv2.cvtColor(resizedFrame, cv2.COLOR_BGR2RGBA)
                    image = Image.fromarray(cv2image)
                    imgtk = ImageTk.PhotoImage(image=image)
                    self.videoPanel.imgtk = imgtk
                    self.videoPanel.configure(image=imgtk)
        self.window.after(int(self.frameInterval * self.rate), self.frameLoop)

    def screenShot(self):
        if not self.cap or not isinstance(self.current_image, numpy.ndarray):
            return
        self.playing = False
        cv2image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGBA)
        image = Image.fromarray(cv2image)
        path = tk.filedialog.asksaveasfilename(
            initialdir=script_dir, filetypes=[("PNG", ".png"), ("JPEG", ".jpg")], defaultextension=".png"
        )
        if not path:
            path = os.path.join(script_dir, f"screenshot_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png")
        image.save(path)
        print("\n========ScreenShot=======")
        print("Saved at", path)
        print("File Type:", path.split(".")[-1])
        print("=========================\n")


root = tk.Tk()
root.title("Video Player")
app = App(root)
app.window.mainloop()
