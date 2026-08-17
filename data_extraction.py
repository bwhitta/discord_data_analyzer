# User interfaces
from tkinter import ttk
# Data analysis
import pandas as pd
import numpy as np
# Time zone management library
import pytz
# File management
import zipfile
import json

def extractFile(filepath, tkWindow, processLabel, userTimezone, logger):
    processLabel.config(text="Extracting data...")

    # Show progress bar using Tkinter
    logger.info("Showing progress bar for extracting file")
    readProgress = ttk.Progressbar(tkWindow, length=300)
    readProgress.grid()
    readProgressLabel = ttk.Label(tkWindow, text="Starting processing channels")
    readProgressLabel.grid()
    
    messageDfs = {}
    channelNames = None
    logger.info(f"Opening zip file at {filepath} as context manager")
    with zipfile.ZipFile(filepath) as zippedFolder:
        # Iterate through files in the zipped folder
        totalFilepaths = len(zippedFolder.namelist())
        i = 0
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
            readProgressLabel.config(text=f"Processed file {i} of {totalFilepaths} in zip")
            pctProgress = i/totalFilepaths
            readProgress["value"]=pctProgress*100
            i += 1
    logger.info(f"Finished finding finding message files. Number of message dataframes: {len(messageDfs)}")

    # Hide progress bar
    readProgress.grid_forget()
    readProgressLabel.grid_forget()
    
    namelessAllMessages = pd.concat(messageDfs, names=["channel_id", "num"])
    logger.info("concatenated messages")
    logger.info(f"Concatenated message dataframes (length {len(namelessAllMessages)})")

    messages = namelessAllMessages.join(channelNames.rename("channel_name"), on="channel_id", how="left")
    logger.info(f"Joined channel names to messages (length {len(messages)})")

    # Make sure the ID doesn't use scientific notation
    messages["ID"] = messages["ID"].astype(int).astype(str)
    logger.info(f"Fixed message ID formatting")

    # Replace blank values in Attachments with NaN
    messages["Attachments"] = messages["Attachments"].replace("", np.nan)
    logger.info(f"Replaced blank attachments with NaN")

    # Format the timestamp
    messages["Timestamp"] = pd.to_datetime(messages["Timestamp"])
    # Change it from un-localized time zone to UTC
    messages["Timestamp"] = messages["Timestamp"].apply(pytz.utc.localize)
    # Convert from UTC to the selected time zone
    messages["Timestamp"] = messages["Timestamp"].apply(lambda f: f.astimezone(userTimezone))
    logger.info(f"Formatted timestamp as datetime and applied time zone")
    
    return messages