from pytube import Playlist
from pytube import YouTube
from os import path
from os import chdir
from os import getcwd
import requests
import threading
import sys

from tkinter import *
from functools import partial

home_dir = getcwd()

class YTRandomizer(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.text = StringVar()
        self.text.set("")
        self.parent = parent
        self.pack()
        YTRandomizer.make_widgets(self)

    def make_widgets(self):
        self.winfo_toplevel().title("Youtube Clip Randomizer")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        enter = Button(self)
        link_entry = Entry(self)
        link_label = Label(self, text="Playlist")
        video_out_entry = Entry(self)
        video_out_label = Label(self, text="Video Output Folder")
        clip_out_entry = Entry(self)
        clip_out_label = Label(self, text="Clip Output Folder")
        feedback_label = Label(self, text="Press Run to Start")
        enter.configure(text="RUN", command=partial(self.thread_cut_videos, enter, link_entry, video_out_entry, clip_out_entry))

        link_label.grid(row=0, column=0)
        link_entry.grid(row=0, column=1)
        video_out_label.grid(row=1, column=0)
        video_out_entry.grid(row=1, column=1)
        clip_out_label.grid(row=2, column=0)
        clip_out_entry.grid(row=2, column=1)
        enter.grid(row=3, column=2)
        feedback_label.grid(row=4, column=2)



    def cut_videos(self, button, pentry, videntry, clipentry):
        print("here1")
        feedback = Label(self, textvariable=self.text)
        feedback.grid(row=4, column=0)
        button.configure(state=DISABLED)
        pentry.configure(state=DISABLED)
        videntry.configure(state=DISABLED)
        clipentry.configure(state=DISABLED)

        link = pentry.get()
        vid_out = videntry.get()
        clip_out = clipentry.get()

        if "youtube.com" in link:
            test_request = requests.get(link)

        if not path.exists(vid_out):
            self.text.set("Video output folder does not exist!")
        elif not path.exists(clip_out):
            self.text.set("Clip output folder does not exist!")
        elif not ("youtube.com" in link):
            self.text.set("Invalid link")
        elif not test_request.status_code == 200:
            self.text.set("Playlist at " + str(link) + " does not exist!")
        else:
            playlist = Playlist(link)
            videos_processed = 1
            chdir(vid_out)
            for video in playlist:
                self.text.set("Downloading video " + str(videos_processed) + "/" + str(len(playlist)))
                try:
                    vid = YouTube(video).streams.filter(res="720p", audio_codec="mp4a.40.2")
                    print(str(YouTube(video).streams.filter(audio_codec="mp4a.40.2")))
                except:
                    print("ERROR HANDLED")
                    try:
                        vid = YouTube(video).streams.get_highest_resolution()
                    except:
                        print("HANDLING FAILED")
                if len(vid) == 0:
                    try:
                        vid = YouTube(video).streams.get_highest_resolution()
                    except:
                        print("HANDLING FAILED 2")

                try:
                    vid[0].download()
                except:
                    try:
                        vid.download()
                    except:
                        print(video)
                videos_processed = videos_processed + 1
        self.text.set("Done")

        button.configure(state=ACTIVE)
        pentry.configure(state=NORMAL)
        videntry.configure(state=NORMAL)
        clipentry.configure(state=NORMAL)

    def thread_cut_videos(self, button, pentry, videntry, clipentry):
        threading.Thread(target=self.cut_videos, args=(button, pentry, videntry, clipentry)).start()





root = Tk()
def kill_all():
    root.destroy()
    exit()
root.protocol("WM_DELETE_WINDOW", kill_all)
APP = YTRandomizer(root)

root.mainloop()






