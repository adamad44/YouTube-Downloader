import tkinter as tk
from tkinter import *
from tkmacosx import Button
from tkinter import filedialog
from tkinter import messagebox
import subprocess, json
import threading
import os

root = tk.Tk()
root.config(width=600, height=600)
root.title("YouTube Downloader")
root.minsize(600, 600)
root.maxsize(600, 600)

global selectedFileContents
global folder_selected
fileList = []
selectedFileContents = ""

# import a list of links from a text file and insert into text box
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

# get the size of a video from a youtube link
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


# calculate the size of all the videos in the list
def calculateSize():
    fileListUpdatedUnflitered = (listBox.get("1.0", END)).split("\n")
    fileListUpdated = []
    for item in fileListUpdatedUnflitered:
        if "youtube" in item:
            fileListUpdated.append(item)
        else:
            pass


    print(fileListUpdated)
    root.after(0, lambda: sizeLabel.config(text="Calculating"))
    root.after(0, lambda: downloadListButton.config(bg="grey", state="disabled"))
    total_size = sum(get_video_size(url) for url in fileListUpdated)
    total = f"Total size of all links: {total_size / (1024 ** 3):.2f} GB"

    
    if total == "0.00 MB":
        total = f"{(get_video_size(listBox.get("1.0", END))) / (1024 ** 2):.2f} MB"
    root.after(0, lambda: sizeLabel.config(text=total))
    root.after(0, lambda: downloadListButton.config(bg="#c7fdff", state="normal"))
    
        
    
# download the list of videos
def downloadList(video_urls):
    if "youtube" in (str(listBox.get("1.0", END)).lower()):

        folder_path = filedialog.askdirectory()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for url in video_urls:
            output_path = os.path.join(folder_path, '%(title)s.%(ext)s')
            command = [
                'yt-dlp',
                '-f', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',  
                '-o', output_path,  
                '--merge-output-format', 'mp4',  
                url
            ]
            output = subprocess.run(command)
    else:
        messagebox.showerror("error", "please enter a link")




# start threads

def start_calculate_size_thread():
    threading.Thread(target=calculateSize).start()

def downloadListThread(video_urls):
    threading.Thread(target=downloadList, args=(video_urls,)).start()




# UI elements

title = Label(text="YouTube Downloader", font="Verdana 23", pady=5)
title.pack()

insertHereLabel = Label(root, text="Enter a link on each line", font="Verdana 12")
insertHereLabel.pack()

listBox = Text(root, bg="white", fg="black", border=None, font="Verdana 15", height=20, width=50)
listBox.pack()

sizeLabel = Label(root, text="", font="Verdana 14", fg="red")
sizeLabel.pack(pady=(1, 1))

buttonFrame = Frame(root)
buttonFrame.pack(pady=(1, 1))

importListButton = Button(buttonFrame, text="Import List", font="Verdana 16 bold", bg="white", fg="black", border=None, command=importList)
importListButton.pack(side=tk.LEFT, anchor=N, padx=(10, 10), ipadx=6, ipady=6, pady=(2, 1))

downloadListButton = Button(buttonFrame, text="Download List", font="Verdana 18 bold", bg="#c7fdff", fg="black", border=None, command=lambda: downloadListThread( (listBox.get("1.0", END)).split("\n") ))
downloadListButton.pack(side=tk.LEFT, anchor=N, padx=(22, 10), ipadx=6, ipady=6, pady=(2, 1))

calculateSizeButton = Button(buttonFrame, text="Calculate Size", font="Verdana 16 bold", bg="white", fg="black", border=None, command=start_calculate_size_thread)
calculateSizeButton.pack(side=tk.LEFT, anchor=N, padx=(15, 10), ipadx=6, ipady=6, pady=(2, 1))




root.mainloop()
