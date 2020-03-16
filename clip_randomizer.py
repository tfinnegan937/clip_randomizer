from pytube import Playlist
from pytube import YouTube
from os import path
from os import chdir
from os import listdir
from os import getcwd
from os import remove
import requests
import threading
import sys
import ffmpeg
from tkinter import *
import tkinter.filedialog as fd
from functools import partial
import moviepy.editor as mp
import math

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
        vid_browse = Button(self)
        clip_browse = Button(self)
        link_entry = Entry(self)
        link_label = Label(self, text="Playlist")
        video_out_entry = Entry(self)
        video_out_label = Label(self, text="Video Output Folder")
        clip_out_entry = Entry(self)
        clip_out_label = Label(self, text="Clip Output Folder")
        feedback_label = Label(self, text="Press Run to Start")
        enter.configure(text="RUN", command=partial(self.thread_cut_videos, enter, link_entry, video_out_entry, clip_out_entry, vid_browse, clip_browse))
        vid_browse.configure(text="Browse", command=partial(self.browseFolders, video_out_entry))
        clip_browse.configure(text="Browse", command=partial(self.browseFolders, clip_out_entry))
        link_label.grid(row=0, column=0)
        link_entry.grid(row=0, column=1)
        video_out_label.grid(row=1, column=0)
        video_out_entry.grid(row=1, column=1)
        vid_browse.grid(row=1, column=2)
        clip_out_label.grid(row=2, column=0)
        clip_out_entry.grid(row=2, column=1)
        clip_browse.grid(row=2, column=2)
        enter.grid(row=3, column=2)
        feedback_label.grid(row=4, column=2)


    def browseFolders(self, field):
        folder = fd.askdirectory()
        field.delete(0, 'end')
        field.insert(0, folder)

    def cut_videos(self, button, pentry, videntry, clipentry, v_browse, c_browse):
        print("here1")
        feedback = Label(self, textvariable=self.text)
        feedback.grid(row=4, column=0)
        button.configure(state=DISABLED)
        pentry.configure(state=DISABLED)
        videntry.configure(state=DISABLED)
        clipentry.configure(state=DISABLED)
        v_browse.configure(state=DISABLED)
        c_browse.configure(state=DISABLED)
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
            for video in playlist:
                self.text.set("Downloading video " + str(videos_processed) + "/" + str(len(playlist)))
                self.download_best(video, vid_out)
                videos_processed = videos_processed + 1
            clips_sliced = 1
            for video in listdir(vid_out):
                self.text.set("Slicing clip " + str(clips_sliced) + "/" + str(len(listdir(vid_out))))
                self.cut_downloaded(video, clip_out, vid_out)
                clips_sliced = clips_sliced + 1
        self.text.set("Done")

        button.configure(state=ACTIVE)
        v_browse.configure(state=ACTIVE)
        c_browse.configure(state=ACTIVE)
        pentry.configure(state=NORMAL)
        videntry.configure(state=NORMAL)
        clipentry.configure(state=NORMAL)

    def thread_cut_videos(self, button, pentry, videntry, clipentry, v_browse, c_browse):
        threading.Thread(target=self.cut_videos, args=(button, pentry, videntry, clipentry, v_browse, c_browse)).start()

    def download_best(self, video, video_out):
        try:
            vid = YouTube(video).streams.filter(adaptive=True, res="720p")[0]
        except:
            vid = YouTube(video).streams.filter(adaptive=True, res="720p")
        try:
            aud = YouTube(video).streams.get_audio_only()[0]
        except:
            aud = YouTube(video).streams.get_audio_only()

        title = YouTube(video).title
        title = title.replace(" ", "-")
        title = title.replace(".", "-")
        title = title.replace("|", "-")
        title = title.replace(":", "-")
        title = title.replace(",", "-")
        audio_name = title + "_aud"
        video_name = title + "_vid"
        try:
            vid.download(output_path=video_out, filename=video_name)
            aud.download(output_path=video_out, filename=audio_name)

            audio_path = video_out + "/" + audio_name + ".mp4"
            video_path = video_out + "/" + video_name + ".mp4"
            print(audio_path)
            print(video_path)

            video_input = mp.VideoFileClip(video_path)

            video_input.write_videofile(video_out + "/" + title + ".mp4", audio=audio_path)
            remove(audio_path)
            remove(video_path)
            video_input.close()
        except:
            try:
                remove(audio_path)
                remove(video_path)
            except:
                print("No video clips to remove")
            YouTube(video).streams.get_highest_resolution().download(output_path=video_out)

    def cut_downloaded(self, clip, clip_out, vid_out):
        clip_name = clip.split(".")[0]
        file = vid_out + "/" + clip

        full_video = mp.VideoFileClip(file)

        secs = full_video.duration
        print("secs: " + str(secs))
        minutes = secs / 60

        minutes = math.floor(minutes)
        print("mins: " + str(minutes))
        for minute in range(0, minutes):
            sub_video = full_video.subclip(minute * 60, (minute + 1) * 60)
            print(str(minute * 60) + "-" + str((minute + 1) * 60))
            print(clip_out + "/" + clip_name + "_" + str(minute) + ".mp4")
            sub_video.write_videofile(clip_out + "/" + clip_name + "_" + str(minute) + ".mp4")
            sub_video.close()
            full_video.close()
            full_video = mp.VideoFileClip(file)

root = Tk()
def kill_all():
    root.destroy()
    exit()
root.protocol("WM_DELETE_WINDOW", kill_all)
APP = YTRandomizer(root)

root.mainloop()






