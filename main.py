import platform
import tkinter as tk
import tkinter.filedialog
from PIL import ImageTk, Image
import vlc
import os


script_dir = os.path.dirname(__file__)


class VideoPlayer:
    def __init__(self, path=None):
        self.media = vlc.MediaPlayer()
        self.media.audio_set_mute(True)
        self.media.video_set_mouse_input(False)

    def openFile(self, uri):
        self.media.set_mrl(uri)

    def play(self, path=None):
        if path:
            self.openFile(path)
        self.media.play()

    def pause(self):
        self.media.pause()

    def getState(self):
        state = self.media.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        return -1

    def getPosition(self):
        return self.media.get_position()

    def setPosition(self, val):
        self.media.set_position(val)

    def getRate(self):
        return self.media.get_rate()

    def setRate(self, rate):
        self.media.set_rate(rate)

    def setWindow(self, wm_id):
        if platform.system() == "Windows":
            self.media.set_hwnd(wm_id)
        else:
            self.media.set_xwindow(wm_id)

    def screenshot(self, path):
        return self.media.video_take_snapshot(
            num=0, psz_filepath=path, i_height=self.media.video_get_height(), i_width=self.media.video_get_width()
        )

    def getLength(self):
        return self.media.get_length()

    def getTime(self):
        return self.media.get_time() / 1000

    def add_callback(self, event_type, callback):
        self.media.event_manager().event_attach(event_type, callback)

    def remove_callback(self, event_type, callback):
        self.media.event_manager().event_detach(event_type, callback)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.player = VideoPlayer()
        self.title("Video Player")
        # Video Canvas
        self._videoCanvas = tk.Canvas(self, bg="black")
        self._videoCanvas.pack(fill="both", expand=True)
        self.player.setWindow(self._videoCanvas.winfo_id())
        # Control Panel
        self.frame = tk.Frame(self)
        self.seekBar = tk.Scale(self.frame, from_=0, to=1000, orient=tk.HORIZONTAL, length=600, showvalue=False,)
        self.seekBar.pack(side=tk.TOP, padx=10)
        self.speedLabel = tk.Label(self.frame, text="Speed: x1.0")
        self.speedLabel.pack(side=tk.LEFT, padx=10)
        tk.Button(self.frame, text="▶", command=lambda: self.control(0)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame, text="Open", command=lambda: self.control(2)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame, text="⏪", command=lambda: self.setRate(0)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame, text="⏩", command=lambda: self.setRate(1)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame, text="screenshot", command=lambda: self.screenshot()).pack(side=tk.LEFT, padx=5)
        self.timerLabel = tk.Label(self.frame, text="")
        self.timerLabel.pack(side=tk.LEFT, padx=10)
        self.frame.pack()
        self.timer()

    def setTime(self, val):
        val = val / 1000
        self.player.setPosition(val)

    def timer(self):
        time = round(self.player.getTime(), None)
        min = int(time / 60)
        sec = time - min * 60

        if time < 0:
            self.seekBar.set(0)
            self.timerLabel.configure(text="")
        else:
            self.seekBar.set(self.player.getPosition() * 1000)
            self.timerLabel.configure(text=f"Time: {round(min, None)}: {round(sec, None)}")
        self.after(100, self.timer)

    def control(self, action):
        if action == 0:
            if self.player.getState() == 1:
                return self.player.pause()
            self.player.play()
        elif action == 2:
            path = tk.filedialog.askopenfilename()
            if path:
                self.player.play(path)
                self.setRate(val=1.0)

    def setRate(self, action=None, val=None):
        if val:
            self.speedLabel.configure(text=f"Speed: x{val}")
            return self.player.setRate(val)
        rate = self.player.getRate()
        if action == 0:
            if rate <= 0.2:
                return
            nextRate = round(rate - 0.2, 1)
        else:
            if rate >= 8:
                return
            nextRate = round(rate + 0.2, 1)
        self.speedLabel.configure(text=f"Speed: x{nextRate}")
        self.player.setRate(nextRate)

    def screenshot(self):
        if self.player.getState() == 1:
            self.player.pause()
        path = tk.filedialog.asksaveasfilename(initialdir=script_dir, filetypes=[("PNG", ".png"), ("JPEG", ".jpg")])
        if path:
            self.player.screenshot(path)


if "__main__" == __name__:
    app = App()
    app.mainloop()
