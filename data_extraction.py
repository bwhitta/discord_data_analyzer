# User interfaces
from tkinter import ttk
# File management
import os
import zipfile
import tempfile
# Data analysis
import pandas as pd
import numpy as np

def extractFile(filepath, tkWindow, processLabel):
    print("Starting file extraction")
    fileZipped = zipfile.ZipFile(filepath)
    
    # Show a looping loading bar
    readProgress = ttk.Progressbar(tkWindow, length=300, mode="indeterminate")
    readProgress.grid()
    readProgress.start()

    processLabel.config(text="Extracting file...")
    with tempfile.TemporaryDirectory() as tempDirectory:
        # Extract the file
        fileZipped.extractall(tempDirectory)
        
        # Hide the loading bar
        readProgress.grid_forget()

        # Turn the message files into a pandas dataframe
        dataFolderName = os.path.splitext(os.path.basename(filepath))[0]
        messages = extractMessages(f"{tempDirectory}/{dataFolderName}", tkWindow, processLabel)
    
    print("Extracting file completed")
    return messages

def extractMessages(rootPath, tkWindow, processLabel):
    messagesPath = f"{rootPath}/Messages"

    # Loop through everything in the "messages" folder
    processLabel.config(text="Gathering channel info...")
    messagesJsonFiles = {}
    channelNamesJson = ""
    for channel in os.listdir(messagesPath):
        filePath = f"{messagesPath}/{channel}"
        # If it's a folder, add the filepath of the location inside to messagesJsonFiles. Otherwise, it must be the channel names JSON and so that filepath is saved
        if os.path.isdir(filePath):
            messagesJsonFiles[channel] = f"{filePath}/messages.json"
        else:
            channelNamesJson = filePath
    
    # Create a dataframe that associates channel IDs with their name
    channelNames = pd.read_json(f"{channelNamesJson}", orient="index")
    channelNames.index = channelNames.index.astype(int).astype(str)
    
    # Turn all of the jsons into pandas dataframes
    messageDfs = readMessageJsons(messagesJsonFiles, tkWindow, processLabel)
    
    # Combine all of the channel dataframes into one big df
    namelessAllMessages = pd.concat(messageDfs, names=["channel_id", "num"])
    
    # Use the data taken from index.json earlier to figure out channel names
    messages = namelessAllMessages.join(channelNames, on="channel_id", how="left")
    messages = messages.rename(columns={0: "channel_name"})
    
    # Make sure the ID doesn't use scientific notation
    messages["ID"] = messages["ID"].astype(int).astype(str)

    # Replace blank values in Attachments with NaN
    messages["Attachments"] = messages["Attachments"].replace("", np.nan)

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