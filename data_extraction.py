# User interfaces
from tkinter import ttk
# File management
import os
import zipfile
import tempfile
import json
# Data analysis
import pandas as pd
import numpy as np

def extractFile(filepath, tkWindow, processLabel):
    processLabel.config(text="Extracting data...")
    # Show progress bar using Tkinter
    readProgress = ttk.Progressbar(tkWindow, length=300)
    readProgress.grid()
    readProgressLabel = ttk.Label(tkWindow, text="Starting processing channels")
    readProgressLabel.grid()
    
    messageDfs = {}
    channelNames = None
    with zipfile.ZipFile(filepath) as zippedFolder:
        # Iterate through files in the zipped folder
        i = 0
        totalMessages = len(zippedFolder.namelist())
        for pathName in zippedFolder.namelist():
            # Find messages.json files and the index.json file
            if (pathName.startswith("Messages") and pathName.endswith("messages.json")):
                # This selector gets rid of Messages/ and .messages.json to just get the channel ID
                channelId = pathName[10:-14]
                # Turn the JSON into a dataframe, then put it in the messageDfs dictionary
                messageJson = json.loads(zippedFolder.read(pathName).decode("utf-8"))
                messageDfs[channelId] = pd.DataFrame(messageJson)
            elif (pathName == "Messages/index.json"):
                # Make a series from the index.json file so that we know channel names
                channelNamesJson = json.loads(zippedFolder.read(pathName).decode("utf-8"))
                channelNames = pd.Series(channelNamesJson)
            
            # Update progress bar
            readProgressLabel.config(text=f"Processed file {i} of {totalMessages} in zip")
            pctProgress = i/totalMessages
            readProgress["value"]=pctProgress*100
            i += 1

    # Hide progress bar
    readProgress.grid_forget()
    readProgressLabel.grid_forget()
    
    namelessAllMessages = pd.concat(messageDfs, names=["channel_id", "num"])

    messages = namelessAllMessages.join(channelNames.rename("channel_name"), on="channel_id", how="left")

    # Make sure the ID doesn't use scientific notation
    messages["ID"] = messages["ID"].astype(int).astype(str)

    # Replace blank values in Attachments with NaN
    messages["Attachments"] = messages["Attachments"].replace("", np.nan)

    messages["Timestamp"] = pd.to_datetime(messages["Timestamp"])

    print(type(messages["Timestamp"]["1365148369080684625"][0]))
    return messages


def readMessageJsons(messageJsons, tkWindow, processLabel):
    # Show UI for number of files read
    readProgress = ttk.Progressbar(tkWindow, length=300)
    readProgress.grid()
    readProgressLabel = ttk.Label(tkWindow, text="Starting processing channels")
    readProgressLabel.grid()

    # Read the messages JSON files
    print("Reading data")
    processLabel.config(text="Gathering channel info...")
    totalMessages = len(messageJsons)
    messageDfs = {}
    i = 0
    for channelFolder, filePath in messageJsons.items():
        # Remove the leading "c" from the folder name to get the channel's ID
        channelId = channelFolder[1:]

        # Turn the JSON into a pandas dataframe
        messageDfs[channelId] = pd.read_json(filePath)

        # Update UI
        i += 1
        readProgressLabel.config(text=f"Processed channel {i} of {totalMessages} (ID {channelId})")
        pctProgress = i/totalMessages
        readProgress["value"]=pctProgress*100
    
    # Hide UI
    readProgress.grid_forget()
    readProgressLabel.grid_forget()

    return messageDfs