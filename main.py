import tkinter as tk
from tkinter import *
from tkmacosx import Button
from tkinter import filedialog
from tkinter import messagebox
import subprocess, json
import threading
import os

root = tk.Tk()
width, height = 600,570
root.config(width=width, height=height)
root.title("YouTube Downloader")
root.minsize(width, height)
root.maxsize(width, height)

global selectedFileContents
global folder_selected
fileList = []
selectedFileContents = ""


def importList():
    try:
        file_selected = filedialog.askopenfilename()
        openedFile = open(file_selected, "r+")
        selectedFileContents = openedFile.read()
        listBox.delete('1.0', END)
        listBox.insert(INSERT, selectedFileContents)
        global fileList
        fileList = selectedFileContents.split("\n")
    except:
        pass

# video size functions
def get_video_size(url):
    command = ['yt-dlp', '-f', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]', '-J', url]
    result = subprocess.run(command, capture_output=True, text=True)
    try:
        metadata = json.loads(result.stdout)
        video_filesize = metadata.get('requested_formats', [{}])[0].get('filesize', 0)
        audio_filesize = metadata.get('requested_formats', [{}])[1].get('filesize', 0)
        return (video_filesize or 0) + (audio_filesize or 0)
    except (json.JSONDecodeError, IndexError, KeyError):
        return 0

def get_video_size_max_quality(url):
    command = ['yt-dlp', '-f', 'bestvideo+bestaudio/best', '-J', url]
    result = subprocess.run(command, capture_output=True, text=True)
    
    try:
        metadata = json.loads(result.stdout)
        video_filesize = metadata.get('requested_formats', [{}])[0].get('filesize', 0)
        audio_filesize = metadata.get('requested_formats', [{}])[1].get('filesize', 0)
        return (video_filesize or 0) + (audio_filesize or 0)
    except (json.JSONDecodeError, IndexError, KeyError):
        return 0

# calculate the size of all the videos in the list
def calculateSize():
    fileListUpdatedUnflitered = (listBox.get("1.0", END)).split("\n")
    fileListUpdated = []
    for item in fileListUpdatedUnflitered:
        if "youtube" in item:
            fileListUpdated.append(item)
        else:
            pass


    root.after(0, lambda: sizeLabel.config(text="Calculating"))
    root.after(0, lambda: downloadListButton.config(bg="grey", state="disabled"))
    total_size = sum(get_video_size(url) for url in fileListUpdated)
    total = f"Total size of all links: {total_size / (1024 ** 3):.2f} GB"

    
    if total == "0.00 MB":
        total = f"{(get_video_size(listBox.get("1.0", END))) / (1024 ** 2):.2f} MB"
    root.after(0, lambda: sizeLabel.config(text=total))
    root.after(0, lambda: downloadListButton.config(bg="#c7fdff", state="normal"))


def downloadList(video_urls):
    if "youtube" in (str(listBox.get("1.0", END)).lower()):
        countOfVideos = 0

        for i in video_urls:
            if "youtube" in i:
                countOfVideos += 1
        folder_path = filedialog.askdirectory()

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        count = 1

        for url in video_urls:
            statusLabel.config(text=f"Status: Downloading video {count}/{countOfVideos}")
            downloadListButton.config(bg="grey", state="disabled")
            output_path = os.path.join(folder_path, '%(title)s.%(ext)s')
            command = [
                'yt-dlp',
                '-f', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',  
                '-o', output_path,  
                '--merge-output-format', 'mp4',  
                url
            ]
            output = subprocess.run(command)
            count += 1
        statusLabel.config(text="Status: Done.")
        downloadListButton.config(bg="#c7fdff", state="normal")
        root.after(5000, changeStatusToReady)

    else:
        messagebox.showerror("error", "please enter a link")

def downloadListMaxQuality(video_urls):
    if "youtube" in (str(listBox.get("1.0", END)).lower()):
        countOfVideos = 0

        for i in video_urls:
            if "youtube" in i:
                countOfVideos += 1
        folder_path = filedialog.askdirectory()

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        count = 1

        for url in video_urls:
            statusLabel.config(text=f"Status: Downloading video {count}/{countOfVideos}")
            downloadListButton.config(bg="grey", state="disabled")
            output_path = os.path.join(folder_path, '%(title)s.%(ext)s')
            command = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  
                '-o', output_path,  
                '--merge-output-format', 'mp4',  
                url
            ]
            output = subprocess.run(command)
            count += 1
        statusLabel.config(text="Status: Done.")
        downloadListButton.config(bg="#c7fdff", state="normal")
        root.after(5000, changeStatusToReady)

    else:
        messagebox.showerror("error", "please enter a link")

def calculateSizeMaxQuality():
    fileListUpdatedUnflitered = (listBox.get("1.0", END)).split("\n")
    fileListUpdated = []

    for item in fileListUpdatedUnflitered:

        if "youtube" in item:
            fileListUpdated.append(item)

        else:
            pass

    root.after(0, lambda: sizeLabel.config(text="Calculating"))
    root.after(0, lambda: downloadListButton.config(bg="grey", state="disabled"))
    total_size = sum(get_video_size_max_quality(url) for url in fileListUpdated)
    total = f"Total size of all links: {total_size / (1024 ** 3):.2f} GB"

    
    if total == "0.00 MB":
        total = f"{(get_video_size(listBox.get("1.0", END))) / (1024 ** 2):.2f} MB"
        
    root.after(0, lambda: sizeLabel.config(text=total))
    root.after(0, lambda: downloadListButton.config(bg="#c7fdff", state="normal"))

# start threads

def start_calculate_size_thread():
    threading.Thread(target=calculateSize).start()

def downloadListThread(video_urls):
    threading.Thread(target=downloadList, args=(video_urls,)).start()

def downloadListThreadMaxQuality(video_urls):
    threading.Thread(target=downloadListMaxQuality, args=(video_urls,)).start()

def changeStatusToReady():
    statusLabel.config(text="Status: Ready")

def start_calculate_size_thread_max_quality():
    threading.Thread(target=calculateSizeMaxQuality).start()

# UI elements

title = Label(text="YouTube Downloader", font="Verdana 26", pady=5)
title.pack()

insertHereLabel = Label(root, text="Enter a full youtube link on each line", font="Verdana 14")
insertHereLabel.pack()

listBox = Text(root, bg="white", fg="black", border=None, font="Verdana 20", height=10, width=40)
listBox.pack()

sizeLabel = Label(root, text="", font="Verdana 18", fg="red")
sizeLabel.pack(pady=(1, 1))



buttonFrame = Frame(root)
buttonFrame.pack(pady=(1, 1))

importListButton = Button(buttonFrame, text="Import List", font="Verdana 15 bold", bg="white", fg="black", border=None, command=importList)
importListButton.pack(side=tk.LEFT, anchor=N, padx=(10, 10), ipadx=6, ipady=6, pady=(2, 1))

downloadListButton = Button(buttonFrame, text="Download List", font="Verdana 15 bold", bg="#c7fdff", fg="black", border=None, command=lambda: downloadListThread( (listBox.get("1.0", END)).split("\n") ))
downloadListButton.pack(side=tk.LEFT, anchor=N, padx=(22, 10), ipadx=6, ipady=6, pady=(2, 1))

calculateSizeButton = Button(buttonFrame, text="Calculate Size", font="Verdana 15 bold", bg="white", fg="black", border=None, command=start_calculate_size_thread)
calculateSizeButton.pack(side=tk.LEFT, anchor=N, padx=(15, 10), ipadx=6, ipady=6, pady=(2, 1))



statusLabel = Label(root, text="Status: Ready", font="Verdana 16", fg="green")
statusLabel.pack(pady=(1, 1))

smallInfoLabel = Label(root, text="Note: videos are downloaded in 1080p by default", font="Verdana 10", fg="grey")
smallInfoLabel.pack(pady=(3, 0))

downloadMaxQualityButton = Button(root, height = 40, text="Download Max Quality", font="Verdana 14 bold", bg="white", fg="black", border=None, command=lambda: downloadListThreadMaxQuality( (listBox.get("1.0", END)).split("\n") ))
downloadMaxQualityButton.pack(pady=(10,1))

calculateSizeMaxQualityButton = Button(root, height = 40, text="Calculate Max Quality File Size", font="Verdana 14 bold", bg="white", fg="black", border=None, command=start_calculate_size_thread_max_quality)
calculateSizeMaxQualityButton.pack(pady=(10,1))
root.mainloop()
