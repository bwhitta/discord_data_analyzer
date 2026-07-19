# User interfaces
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# Data analysis
import pandas as pd
import numpy as np
# Threading for separating UI and processing
import threading
# Time zone management library
import pytz
# Other scripts from this directory
import data_extraction
import data_analysis

def fileSelection():
    # Prompt the user to open a file
    selectedFile = filedialog.askopenfile(filetypes=[("ZIP files", ".zip")])
    if (selectedFile is None):
        print("No file was selected")
        return
    
    # Hide the open button since a file has been found
    openButton.grid_forget()

    # Ask for user's time zone
    processLabel.config(text="Select your timezone.")
    timezone, removeTzSelector = inputTimezone(window)
    
    # Event called when user confirms settings
    def settingsSelected():
        if (timezone.get()==""):
            messagebox.showwarning(message="Please select your timezone.")
            return
        
        usedTimezone = pytz.timezone(timezone.get())

        # Hide settings UI
        removeTzSelector()
        saveSettings.grid_forget()

        # Start processing on another thread
        threading.Thread(target=processingThread, args=(selectedFile.name, window, usedTimezone)).start()
    
    # Add confirm setting button with event
    saveSettings = ttk.Button(window, text='Confirm settings', command=settingsSelected)
    saveSettings.grid()

def processingThread(filepath, tkWindow, userTimezone):
    print("Starting processing thread")
    
    # If anything else in the program throws an error then it will be displayed as a tkinter popup before exiting.
    try: 
        processingData(filepath, tkWindow, userTimezone)
    except Exception as error:
        tk.messagebox.showerror("An error occurred!", f"Error: {error}")
        tkWindow.quit()

def processingData(filepath, tkWindow, userTimezone):
    # Extract the zip file and put the z into a dataframe
    messages = data_extraction.extractFile(filepath, tkWindow, processLabel)
    
    # Fix the timestamp
    # Change it from un-localized time zone to UTC
    messages["Timestamp"] = messages["Timestamp"].apply(pytz.utc.localize)
    messages["Timestamp"] = messages["Timestamp"].apply(lambda f: f.astimezone(userTimezone))

    # Turn the data into visualizations
    data_analysis.analyzeData(messages, tkWindow, processLabel)

def inputTimezone(tkWindow):
    # pytz is tecnically deprecated, but newer alternatives don't include a list like this and so would require some sort of external library
    # Get a list of common timezones
    timezones = pd.Series(pytz.common_timezones)
    
    # Split into region/location
    timezonesDesc = timezones.str.split("/", n=1, expand=True).rename({0:"region", 1:"loc"}, axis=1)
    timezonesDesc["loc"] = timezonesDesc["loc"].str.replace("_", " ")
    timezones = pd.concat([timezones.rename("timezone"), timezonesDesc], axis=1)
    
    # Region selector
    regionLabel = ttk.Label(text="Timezone region")
    regionLabel.grid()
    regionSelector = ttk.Combobox(tkWindow, textvariable=tk.StringVar(), state="readonly")
    regionSelector.grid()
    # Put US at the start of the list (since America is a seperate option)
    regions = timezones["region"].unique()
    regionsOrdered = np.concatenate([["US"], np.delete(regions, np.where(regions == "US"))])
    regionSelector["values"] = list(regionsOrdered)
    
    # Location selector
    locLabel = ttk.Label(text="Timezone location")
    locLabel.grid()
    locSelector = ttk.Combobox(tkWindow, textvariable=tk.StringVar(), state="readonly")
    locSelector.grid()
    
    # Mutable variable for the timezone associated with the current selection
    selectedTimezone = tk.StringVar()

    # Callbacks for when region and location are selected
    def tzRegionSelected(_):
        # Update displayed locations
        dfSubset = timezones[timezones["region"] == regionSelector.get()]
        locSelector["values"] = list(dfSubset["loc"])
    def tzLocSelected(_):
        # Update current selected timezone
        dfSubset = timezones[timezones["region"] == regionSelector.get()]
        timezoneNarrowed = dfSubset[dfSubset["loc"] == locSelector.get()]
        selectedTimezone.set(list(timezoneNarrowed["timezone"])[0])

    # Set up the callbacks
    regionSelector.bind("<<ComboboxSelected>>", tzRegionSelected)
    locSelector.bind("<<ComboboxSelected>>", tzLocSelected)
    
    # Method to hide all of the UI once settings are confirmed
    def removeSelector():
        regionLabel.grid_forget()
        regionSelector.grid_forget()
        locLabel.grid_forget()
        locSelector.grid_forget()
    
    return selectedTimezone, removeSelector

# Create the window
window = tk.Tk()
window.title("test app")
window.geometry("600x300")

# Label used to display info about what is going on
processLabel = ttk.Label(window, text="Select the .zip file of your discord data.")
processLabel.grid()

# File selection button
openButton = ttk.Button(window, text="Choose File", command=fileSelection)
openButton.grid()

# Keep the window refreshing
window.mainloop()