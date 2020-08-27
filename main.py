from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox
from datetime import datetime
import cv2
import os
import numpy

script_dir = os.path.dirname(__file__)


class VideoPlayer(tk.Frame):
    def __init__(self, master, cameraNum=0, videoSize=(1280, 720)):
        super().__init__(master=master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        #
        self.cap = None
        self.currentImage = None
        # Status
        self.cameraNum = cameraNum
        self.videoSize = (videoSize[0], videoSize[1] - 50)
        self.isPlaying = False
        self.isVideo = False
        self.totalFrame = 0
        self.frameCount = 0
        self.fps = 1
        self.frameInterval = 10
        self.rate = 1
        self.nowTimeString = ""
        self.totalTimeString = ""

        self.display = tk.Canvas(self, bd=0, highlightthickness=0, bg="black")
        self.display.grid(row=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.pack(fill=tk.BOTH, expand=1)

        self.startupBG = Image.open(os.path.join(script_dir, "assets/startup.jpg"))
        self.startupResized = self.startupBG.resize(self.videoSize, Image.ANTIALIAS)
        self.startupResized = ImageTk.PhotoImage(self.startupResized)
        self.display.delete("VID")
        self.display.create_image(
            0, 0, image=self.startupResized, anchor=tk.NW, tags="VID"
        )

        self.loadUI()
        self.drawUI()

        self.master.bind("<Key>", self.key)
        self.master.bind("<Button-1>", self.click)
        self.bind("<Configure>", self.resize)
        self.frameLoop()

    def resize(self, event):
        self.videoSize = (event.width, event.height - 50)
        if not self.isPlaying:
            self.startupResized = self.startupBG.resize(self.videoSize, Image.ANTIALIAS)
            self.startupResized = ImageTk.PhotoImage(self.startupResized)
            self.display.delete("VID")
            self.display.create_image(
                0, 0, image=self.startupResized, anchor=tk.NW, tags="VID"
            )
        self.drawUI()

    def useCamera(self):
        self.cap = cv2.VideoCapture(self.cameraNum)
        self.frameCount = 0
        self.totalFrame = -1
        self.isVideo = False
        self.frameInterval = 10
        self.rate = 1
        self.isPlaying = True
        print("\n==========Camera=========")
        print("Camera ID:", self.cameraNum)
        print("Frames Wait Time:", self.frameInterval)
        print("=========================\n")

    def handleOpen(self):
        path = tk.filedialog.askopenfilename()
        if path:
            if path.split(".")[-1].lower() in [
                "mkv",
                "mp4",
                "avi",
                "mov",
                "mpeg",
                "flv",
                "wmv",
            ]:
                self.openFile(path)
            else:
                tk.messagebox.showinfo("無法開啟檔案", "此檔案不是支援的影片檔")

    def openFile(self, path: str):
        self.cap = cv2.VideoCapture(path)
        self.frameCount = 0
        self.getDetails()
        self.isVideo = True
        self.isPlaying = True
        print("\n==========Video==========")
        print("File:", path)
        print("File Type:", path.split(".")[-1])
        print("FPS:", self.fps)
        print("Total Frames:", self.totalFrame)
        print("Video Length:", self.totalTimeString.replace(" / ", ""))
        print(f"Frame Interval: {self.frameInterval}ms")
        print("=========================\n")

    def getDetails(self):
        self.totalFrame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frameInterval = int(500 / self.fps)
        self.rate = 1
        s = int(self.totalFrame / self.fps)
        m = int(s / 60)
        s -= m * 60
        self.totalTimeString = " / {:02d}:{:02d}".format(m, s)

    def setRate(self, val: float):
        if not self.isVideo or not self.isPlaying:
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

    def jumpTo(self, value: int):
        if not self.cap or not isinstance(self.currentImage, numpy.ndarray):
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)
        self.frameCount = value
        s = int(self.frameCount / self.fps)
        m = int(s / 60)
        s -= m * 60
        self.nowTimeString = "{:02d}:{:02d}".format(m, s)
        self.drawUI()
        print("\n========Jump To========")
        print("Time:", "{:02d}:{:02d}".format(m, s))
        print("=========================\n")

    def frameLoop(self):
        if self.frameCount == self.totalFrame:
            self.isPlaying = False
            self.drawUI()
        if self.isPlaying:
            self.cap.grab()
            self.frameCount += 1
            # skip 1 frame for better performance
            # if self.frameCount % 2 == 0:
            if True:
                s = int(self.frameCount / self.fps)
                m = int(s / 60)
                s -= m * 60
                self.nowTimeString = "{:02d}:{:02d}".format(m, s)
                ok, self.currentImage = self.cap.retrieve()
                if ok:
                    resizedFrame = cv2.resize(self.currentImage, (self.videoSize))
                    cv2image = cv2.cvtColor(resizedFrame, cv2.COLOR_BGR2RGBA)
                    image = Image.fromarray(cv2image)
                    self.imgtk = ImageTk.PhotoImage(image)
                    self.display.delete("VID")
                    self.display.create_image(
                        0, 0, image=self.imgtk, anchor=tk.NW, tags="VID"
                    )
                    self.drawUI()
        self.after(int(self.frameInterval * self.rate), self.frameLoop)

    def screenShot(self):
        if not self.cap or not isinstance(self.currentImage, numpy.ndarray):
            return
        self.isPlaying = False
        self.drawUI()
        cv2image = cv2.cvtColor(self.currentImage, cv2.COLOR_BGR2RGBA)
        image = Image.fromarray(cv2image)
        path = tk.filedialog.asksaveasfilename(
            initialdir=script_dir,
            filetypes=[("PNG", ".png"), ("JPEG", ".jpg")],
            defaultextension=".png",
        )
        if not path:
            path = os.path.join(
                script_dir, f"screenshot_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
            )
        image.save(path)
        print("\n========ScreenShot=======")
        print("Saved at", path)
        print("File Type:", path.split(".")[-1])
        print("=========================\n")

    def key(self, event):
        print("pressed", event.keycode)

    def click(self, event):
        if event.y in range(self.videoSize[1]+20, self.videoSize[1] + 50):
            if event.x in range(
                int(self.videoSize[0] / 2 - 12), int(self.videoSize[0] / 2 + 12)
            ):
                print("Play")
                self.isPlaying = not self.isPlaying
                self.drawUI()
            elif event.x in range(
                int(self.videoSize[0] / 2 - 62), int(self.videoSize[0] / 2 - 38)
            ):
                print("backfard")
                self.setRate(+0.2)
            elif event.x in range(
                int(self.videoSize[0] / 2 - 112), int(self.videoSize[0] / 2 - 88)
            ):
                print("import")
                self.handleOpen()
            elif event.x in range(
                int(self.videoSize[0] / 2 - 162), int(self.videoSize[0] / 2 - 138)
            ):
                print("camera")
                self.useCamera()
            elif event.x in range(
                int(self.videoSize[0] / 2 + 38), int(self.videoSize[0] / 2 + 62)
            ):
                print("forward")
                self.setRate(-0.2)
            elif event.x in range(
                int(self.videoSize[0] / 2 + 88), int(self.videoSize[0] / 2 + 112)
            ):
                print("go back")
                self.jumpTo(0)
            elif event.x in range(
                int(self.videoSize[0] / 2 + 138), int(self.videoSize[0] / 2 + 162)
            ):
                print("export")
                self.screenShot()
        if self.cap or isinstance(self.currentImage, numpy.ndarray):
            if event.y in range(self.videoSize[1]-10, self.videoSize[1] + 5):
                print("process")
                percent =event.x / self.videoSize[0]
                self.jumpTo(int(self.totalFrame * percent))
                self.drawUI()

        print("clicked at", event.x, event.y)

    def loadUI(self):
        source_bar = Image.open(os.path.join(script_dir, "assets/bar_withLine.png"))
        source_bar = source_bar.resize((400, 100), Image.ANTIALIAS)
        self.barUI = ImageTk.PhotoImage(source_bar)

        playImg = Image.open(os.path.join(script_dir, "assets/play.png"))
        playImg = playImg.resize((25, 25), Image.ANTIALIAS)
        self.playUI = ImageTk.PhotoImage(playImg)

        pauseImg = Image.open(os.path.join(script_dir, "assets/pause.png"))
        pauseImg = pauseImg.resize((25, 25), Image.ANTIALIAS)
        self.pauseUI = ImageTk.PhotoImage(pauseImg)

        backwardImg = Image.open(os.path.join(script_dir, "assets/fast-backward.png"))
        backwardImg = backwardImg.resize((25, 25), Image.ANTIALIAS)
        self.backwardUI = ImageTk.PhotoImage(backwardImg)

        forwardImg = Image.open(os.path.join(script_dir, "assets/fast-forward.png"))
        forwardImg = forwardImg.resize((25, 25), Image.ANTIALIAS)
        self.forwardUI = ImageTk.PhotoImage(forwardImg)

        exportImg = Image.open(os.path.join(script_dir, "assets/file-export.png"))
        exportImg = exportImg.resize((25, 25), Image.ANTIALIAS)
        self.exportUI = ImageTk.PhotoImage(exportImg)

        importImg = Image.open(os.path.join(script_dir, "assets/file-import.png"))
        importImg = importImg.resize((25, 25), Image.ANTIALIAS)
        self.importUI = ImageTk.PhotoImage(importImg)

        cameraImg = Image.open(os.path.join(script_dir, "assets/camera.png"))
        cameraImg = cameraImg.resize((25, 25), Image.ANTIALIAS)
        self.cameraUI = ImageTk.PhotoImage(cameraImg)

        gobackImg = Image.open(os.path.join(script_dir, "assets/undo.png"))
        gobackImg = gobackImg.resize((25, 25), Image.ANTIALIAS)
        self.gobackUI = ImageTk.PhotoImage(gobackImg)

        circleImg = Image.open(os.path.join(script_dir, "assets/circle.png"))
        circleImg = circleImg.resize((15, 15), Image.ANTIALIAS)
        self.circleUI = ImageTk.PhotoImage(circleImg)

    def drawUI(self):
        self.display.delete("BAR")
        # self.display.create_image(
        #     self.videoSize[0] / 2,
        #     self.videoSize[1],
        #     image=self.barUI,
        #     anchor=tk.S,
        #     tags="BAR",
        # )
        if self.isPlaying:
            self.display.create_image(
                self.videoSize[0] / 2,
                self.videoSize[1] + 40,
                image=self.pauseUI,
                anchor=tk.S,
                tags="BAR",
            )
        else:
            self.display.create_image(
                self.videoSize[0] / 2,
                self.videoSize[1] + 40,
                image=self.playUI,
                anchor=tk.S,
                tags="BAR",
            )
        self.display.create_image(
            self.videoSize[0] / 2 - 150,
            self.videoSize[1] + 40,
            image=self.cameraUI,
            anchor=tk.S,
            tags="BAR",
        )
        self.display.create_image(
            self.videoSize[0] / 2 - 100,
            self.videoSize[1] + 40,
            image=self.importUI,
            anchor=tk.S,
            tags="BAR",
        )
        self.display.create_image(
            self.videoSize[0] / 2 - 50,
            self.videoSize[1] + 40,
            image=self.backwardUI,
            anchor=tk.S,
            tags="BAR",
        )
        self.display.create_image(
            self.videoSize[0] / 2 + 50,
            self.videoSize[1] + 40,
            image=self.forwardUI,
            anchor=tk.S,
            tags="BAR",
        )
        self.display.create_image(
            self.videoSize[0] / 2 + 100,
            self.videoSize[1] + 40,
            image=self.gobackUI,
            anchor=tk.S,
            tags="BAR",
        )
        self.display.create_image(
            self.videoSize[0] / 2 + 150,
            self.videoSize[1] + 40,
            image=self.exportUI,
            anchor=tk.S,
            tags="BAR",
        )
        if self.isVideo:
            self.display.create_text(
                self.videoSize[0] / 2 + 240,
                self.videoSize[1] + 40,
                text=self.nowTimeString + self.totalTimeString,
                font=("Arial", 10),
                fill="white",
                anchor=tk.S,
                tags="BAR",
            )
            processX = (self.frameCount / self.totalFrame) * self.videoSize[0]
            self.display.create_image(
                processX,
                self.videoSize[1]+7,
                image=self.circleUI,
                anchor=tk.S,
                tags="BAR",
            )


root = tk.Tk()
root.title("Video Player")
root.geometry("1280x720")
app = VideoPlayer(root)
app.mainloop()
