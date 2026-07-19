# User interfaces
from tkinter import ttk
# File management
import os
# Data analysis
import pandas as pd
import numpy as np
# Processing text data
import re
# Data visualization
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.font_manager as fm
# Misc. libraries
from cycler import cycler
import collections

# Color palette for associating a color with each year. It's really sick that you can use the XKCD color name survey options here
yearsPalette = cycler("color", ["red", "xkcd:pumpkin orange", "xkcd:goldenrod", "green", "blue", "xkcd:purpley pink", "xkcd:pink"])

def analyzeData(messages, tkWindow, processLabel):
    def updateLabel(processDesc):
        processLabel.config(text=f"Visualizing data ({processDesc})...")

    # Create the results folder if it's missing (since a lot of places, including github, don't like empty folders)
    createResultsFolder()

    # Set up fonts and default styles
    configStyles()

    # Start analyzing and plotting
    messagesBasicInfo(messages, updateLabel)
    plotLetters(messages, updateLabel)
    plotMessageTimes(messages, updateLabel)
    plotMessageLengths(messages, updateLabel)
    plotWords(messages, tkWindow, updateLabel)
    
    # Display results path (and open in file explorer if on windows)
    openFileExplorer(processLabel)

def configStyles():
    # This makes it so MPL is set up to only write files (which is all this program does)
    # If not configured like this it gets mad that it's not run on the main thread
    mpl.use('agg')

    # Set up some default formatting for MPL
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.prop_cycle"] = cycler("color", ["xkcd:green", "xkcd:orangish red", "xkcd:dark sky blue"])
    
    # Find the location of the font
    rootFolder = os.path.dirname(__file__)
    fontPath = f"{rootFolder}/resources/Poppins-Regular.ttf"
    # Add the font and set it as default
    fm.fontManager.addfont(fontPath)
    plt.rcParams["font.family"] = "Poppins"
def savePlot(name, rasterDpi=150):
    print(f"Saving plot '{name}'")
    # Save to the folder in two formats
    rootFolder = os.path.dirname(__file__)
    savePath = f"{rootFolder}/results"
    plt.savefig(f"{savePath}/{name}.svg", transparent=True, bbox_inches="tight")
    plt.savefig(f"{savePath}/{name}.png", dpi=rasterDpi, bbox_inches="tight")
    plt.close()
def createResultsFolder():
    rootFolder = os.path.dirname(__file__)
    resultsFolderPath = f"{rootFolder}/results"
    if not os.path.exists(resultsFolderPath):
        os.mkdir(resultsFolderPath)
def useGreatestTimeUnit(minutes):
    if (minutes >= 60*24*365.25):
        return f"{round(minutes/(60*24*365.25), 1)} years"
    elif (minutes >= 60*24):
        return f"{round(minutes/(60*24), 1)} days"
    elif (minutes >= 60):
        return f"{round(minutes/(60), 1)} hours"
    else:
        return f"{round(minutes)} minutes"

def messagesBasicInfo(messages, updateLabel):
    updateLabel("message counts")
    fig, ax = plt.subplots()
    ax.set_axis_off()

    # Total messages
    ax.set_title(f"{len(messages):,} total messages sent")
    
    # Sending time calculations
    sendingTimeMinutes = len(messages)/4
    sendingTime = useGreatestTimeUnit(sendingTimeMinutes)

    hoursToCrossUS = 42
    drivingComparison = (sendingTimeMinutes/60)/hoursToCrossUS
    drivingComparison = round(drivingComparison, (2 if drivingComparison<5 else 0))
    
    filmLength = 94
    filmComparison = sendingTimeMinutes/filmLength
    filmComparison = round(filmComparison, (1 if filmComparison<5 else 0))
    
    # Total messages with attachments
    hasAttachment = messages["Attachments"].notnull().value_counts()

    # Display the info
    info1 = f"If each of your messages took 15 seconds, sending them would total {sendingTime}. That's roughly equal to driving coast-to-coast across the US {drivingComparison:,} times, without stopping, or watching the film The Neverending Story {filmComparison:,} times."
    info2 = f"{hasAttachment[True]} of those had attachments such as images or files, leaving {hasAttachment[False]} more without."
    ax.text(0, 0.95, f"{info1}\n\n{info2}", horizontalalignment="left", verticalalignment="top", wrap=True)

    savePlot("messages_basic_info")

def plotLetters(messages, updateLabel):
    # Get usage counts by character
    updateLabel("counting characters")
    characterCounts = countCharacters(messages)
    charactersBasicInfo(characterCounts.sum())
    
    # Filter to only letters
    updateLabel("filtering letters")
    letters = "abcdefghijklmnopqrstuvwxyz"
    letterCounts = characterCounts[characterCounts.index.map(lambda f: f in letters)]
    letterCounts = letterCounts.sort_values(ascending=False)
        
    plotLetterFreq(letterCounts)
    updateLabel("comparing letter frequencies")
    compareLetterFreq(letterCounts)
def countCharacters(messages):
    # Combine all message contents to one large string
    combinedMessages = str.join("", messages["Contents"].astype(str).tolist())
    
    # Count number of times each character appears in that string
    characterCounts = pd.Series(collections.Counter(combinedMessages.lower()))
    
    return characterCounts
def charactersBasicInfo(numCharacters):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    
    # Total characters
    ax.set_title(f"{numCharacters:,} total characters of text")
    
    # Stats about total characters
    # Book lengths taken from royalty free books from Project Gutenberg
    bibleLength = 4232659
    aliceInWonderlandLength = 147323
    ravenLength = 6448

    bookLengths = ""
    if numCharacters >= bibleLength:
        bookLengths = f"{round(numCharacters/bibleLength, 1)} copies of the Bible"
    elif numCharacters >= aliceInWonderlandLength:
        bookLengths = f"{round(numCharacters/aliceInWonderlandLength, 1)} copies of Alice in Wonderland by Lewis Carroll"
    else:
        bookLengths = f"{round(numCharacters/ravenLength, 1)} copies of The Raven by Edgar Allan Poe"

    # Distance spanned
    # 12 pt courier new is 10 characters/inch
    distanceInches = numCharacters/10
    fieldLength = 300*12
    billLength = 6.14
    distance = ""
    altDistance = ""
    if distanceInches >= 12*5280:
        distance = f"{round(distanceInches/(12*5280), 1)} miles"
        altDistance = f"{round(distanceInches/fieldLength), 1} football fields"
    else:
        distance = f"{round(distanceInches/12)} feet"
        altDistance = f"{round(distanceInches/billLength)} dollar bills"
    
    # Display the info
    info1 = f"That's equal to " + bookLengths
    info2 = f"If everything you typed was printed using 12pt Courier New (a very common monospaced font), it would stretch for {distance}, which is the length of {altDistance}."
    
    ax.text(0, 0.95, f"{info1}\n\n{info2}", horizontalalignment="left", verticalalignment="top", wrap=True)

    savePlot("characters_basic_info")
def plotLetterFreq(letterCounts):    
    # Temporarily change default plot size
    plt.rcParams["figure.figsize"] = (6.4, 6.4)
    
    # Display letters on a horizontal lollipop plot or bar chart
    ax = plt.subplot()

    # Display te chart
    ax.stem(letterCounts, orientation="horizontal", basefmt="")
    ax.invert_yaxis()

    # Show letters
    ax.set_yticks(range(len(letterCounts)), letterCounts.index)

    # Add commas to x tick values
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda f, _: format(int(f), ",")))

    # Remove outline
    ax.spines[["top","right"]].set_visible(False)

    # Title
    ax.set_title(f"Letters by frequency of use", loc="center")

    # Save and show
    savePlot("letter_freq")

    # Reset to the default plot size
    plt.rcParams["figure.figsize"] = mpl.rcParamsDefault["figure.figsize"]
def compareLetterFreq(letterCounts):
    # Get the percentage of total letters for each letter
    letterPcts = letterCounts.map(lambda f: f/letterCounts.sum())

    # Letter frequency data for comparison
    # Data source: https://books.google.com/books?id=CyCcRAm7eQMC&pg=PA36#v=onepage&q&f=false
    controlLetters = {"a":0.0820,"b":0.0150,"c":0.0280,"d":0.0430,"e":0.1270,"f":0.0220,"g":0.0200,"h":0.0610,"i":0.0700,"j":0.0016,"k":0.0077,"l":0.0400,"m":0.0240,"n":0.0670,"o":0.0750,"p":0.0190,"q":0.0012,"r":0.0600,"s":0.0630,"t":0.0910,"u":0.0280,"v":0.0098,"w":0.0240,"x":0.0015,"y":0.0200,"z":0.0007}
    controlLetters = pd.Series(controlLetters)

    mergedLetters = pd.merge(letterPcts.rename("discord_msg_freq"), controlLetters.rename("control_freq"), left_index=True, right_index=True)
    mergedLetters = mergedLetters.sort_values(by="discord_msg_freq", ascending=False)
    
    # Temporarily change default plot size
    plt.rcParams["figure.figsize"] = (6.4, 6.4)

    ax = plt.subplot()

    # Display the chart
    ax.stem(mergedLetters["control_freq"], orientation="horizontal", linefmt="r:",  markerfmt="r|", basefmt="r", label="Control Data")
    ax.stem(mergedLetters["discord_msg_freq"], orientation="horizontal", markerfmt="|", basefmt="", label="Discord Messages")
    ax.invert_yaxis()

    # Show ticks and legend
    ax.set_yticks(range(len(letterCounts)), letterCounts.index)
    ax.legend()

    # Format as percent
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=0))

    # Remove outline
    ax.spines[["top","right"]].set_visible(False)

    # Title
    ax.set_title("Letters by frequency of use (comparison)", loc="center")
    ax.set_xlabel("Control data is from Cryptological Mathematics by Robert Edward Lewand", size=8)

    # Save and show
    savePlot("letter_freq_2")
    
    # Reset to the default plot size
    plt.rcParams["figure.figsize"] = mpl.rcParamsDefault["figure.figsize"]

hoursDesc = ["12am","1am","2am","3am","4am","5am","6am","7am","8am","9am","10am","11am","12pm","1pm","2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm","10pm","11pm"]
def plotMessageTimes(messages, updateLabel):
    # Use those formatted times for plotting
    updateLabel("messages by month")
    messagesByMonth(messages)
    updateLabel("messages by hour")
    messagesByHour(messages)
    updateLabel("messages by hour annually")
    messagesByHourAnnual(messages)
def messagesByMonth(messages):
    messagesMonthly = pd.crosstab(messages["Timestamp"].dt.year, messages["Timestamp"].dt.month)

    # Add rows for months that never had a message
    messagesMonthly = messagesMonthly.reindex(np.arange(1, 13), axis=1, fill_value=0)
    
    # Turn into a Series with two indexes (month and year)
    messagesMonthly = messagesMonthly.T.stack().sort_index(level=1)

    # Reformat the indexes into one index using format MM/YY
    messagesMonthly.index = messagesMonthly.index.map(lambda f: f"{f[0]}/{str(f[1])[2:]}")

    # Plot the data
    ax = plt.subplot()
    ax.plot(messagesMonthly)
    
    # Label every January
    xticks = pd.Series(messages["Timestamp"].dt.year.unique()).apply(lambda f: f"1/{str(f)[2:]}")
    ax.set_xticks(xticks)
    ax.grid(True,axis="x")
    
    # Remove outline
    ax.spines[["top","right"]].set_visible(False)
    
    # Title
    ax.set_title("Messages sent by month", loc="left")

    savePlot("message_months")
def messagesByHour(messages):
    messagesByHour = messages["Timestamp"].dt.hour.value_counts().sort_index(ascending=False)
    
    # Add rows for months that never had a message
    messagesByHour = messagesByHour.reindex(np.arange(0, 24), axis=1, fill_value=0)

    # Format indexes
    messagesByHour.index = messagesByHour.index.map(lambda f: hoursDesc[f])

    # Calculate numbers for polar histogram
    theta = np.linspace(0.0, 2 * np.pi, len(messagesByHour), endpoint=False)
    radii = messagesByHour
    width = (2*np.pi) / len(messagesByHour)

    # Plot the data
    ax = plt.subplot(111, polar=True)
    ax.bar(theta, radii, width=width)

    # Formatting
    ax.set_xticks(theta, messagesByHour.index, size=10, position=(0,-0.02))
    ax.set_yticks([])
    ax.set_title(f"Messages sent by hour", loc="left")

    savePlot("messages_clock")
def messagesByHourAnnual(messages):
    messageHoursByYear = pd.crosstab(messages["Timestamp"].dt.year, messages["Timestamp"].dt.hour)
    
    # Add rows for months that never had a message
    messageHoursByYear = messageHoursByYear.reindex(np.arange(0, 24), axis=1, fill_value=0)
    
    # Reformat indexes
    messageHoursByYear.columns = messageHoursByYear.columns.map(lambda f: hoursDesc[f])

    # Create a plot for each year
    yearsUsed = messages["Timestamp"].dt.year.unique()
    for year, yearColor in zip(yearsUsed, yearsPalette):
        messagesByHour = messageHoursByYear.loc[year]

        # Calculate numbers for polar histogram
        theta = np.linspace(0.0, 2 * np.pi, len(messagesByHour), endpoint=False)
        radii = messagesByHour
        width = (2*np.pi) / len(messagesByHour)

        # Plot the data
        ax = plt.subplot(111, polar=True)
        ax.bar(theta, radii, width=width, color=yearColor["color"])

        # Formatting
        ax.set_xticks(theta, messagesByHour.index, size=10, position=(0,-0.02))
        ax.set_yticks([])

        # Text
        ax.set_title(f"Messages by hour for {year}", loc="left")
        plt.figtext(0.75,0.9,f"Total Messages:\n{messagesByHour.sum()}")

        savePlot(f"messages_clock_{year}")

def plotMessageLengths(messages, updateLabel):
    updateLabel("message lengths by month")
    messageLengthsByMonth(messages)
    updateLabel("message lengths by hour")
    messageLenthsByHour(messages)
    updateLabel("message lengths by hour annually")
    messagesLengthsByHourAnnual(messages)
def messageLengthsByMonth(messages):
    lengthsByMonth = pd.crosstab(messages["Timestamp"].dt.year, messages["Timestamp"].dt.month, values=messages["Contents"].str.len(), aggfunc="mean")
    lengthsByMonth = lengthsByMonth.fillna(0)

    # Add rows for months that never had a message
    lengthsByMonth = lengthsByMonth.reindex(np.arange(1, 13), axis=1, fill_value=0)
    
    # Turn into a Series with two indexes (month and year)
    lengthsByMonth = lengthsByMonth.T.stack().sort_index(level=1)
    
    # Reformat the indexes into one index using format MM/YY
    lengthsByMonth.index = lengthsByMonth.index.map(lambda f: f"{f[0]}/{str(f[1])[2:]}")

    # Plot the data
    ax = plt.subplot()
    ax.plot(lengthsByMonth)

    # Label every January
    xticks = pd.Series(messages["Timestamp"].dt.year.unique()).apply(lambda f: f"1/{str(f)[2:]}")
    ax.set_xticks(xticks)
    ax.grid(True, axis="x")

    # Remove outline
    ax.spines[["top","right"]].set_visible(False)

    # Title
    ax.set_title("Messages lengths by month", loc="left")
    
    savePlot("message_months_lengths")
def messageLenthsByHour(messages):
    messageLengths = pd.concat([messages, messages["Contents"].str.len().rename("message_len")], axis=1)
    lengthsByHour = messageLengths.groupby(messageLengths["Timestamp"].dt.hour)["message_len"].mean()
    
    # Add rows for months that never had a message
    lengthsByHour = lengthsByHour.reindex(np.arange(0, 24), axis=1, fill_value=0)

    # Reformat indexes
    lengthsByHour.index = lengthsByHour.index.map(lambda f: hoursDesc[f])

    # Calculate numbers for polar histogram
    theta = np.linspace(0.0, 2 * np.pi, len(lengthsByHour), endpoint=False)
    radii = lengthsByHour
    width = (2*np.pi) / len(lengthsByHour)

    # Plot the data
    ax = plt.subplot(111, polar=True)
    ax.bar(theta, radii, width=width)

    # Formatting
    ax.set_xticks(theta, lengthsByHour.index, size=10, position=(0,-0.02))
    ax.set_title(f"Message lengths by hour", loc="left")

    savePlot("message_lengths_clock")
def messagesLengthsByHourAnnual(messages):
    lengthsHourlyByYear = pd.crosstab(messages["Timestamp"].dt.year, messages["Timestamp"].dt.hour, values=messages["Contents"].str.len(), aggfunc="mean")
    lengthsHourlyByYear = lengthsHourlyByYear.fillna(0)

    # Add rows for months that never had a message
    lengthsHourlyByYear = lengthsHourlyByYear.reindex(np.arange(0, 24), axis=1, fill_value=0)

    # Reformat indexes
    lengthsHourlyByYear.columns = lengthsHourlyByYear.columns.map(lambda f: hoursDesc[f])

    # Create a plot for each year
    yearsUsed = messages["Timestamp"].dt.year.unique()
    for year, yearColor in zip(yearsUsed, yearsPalette):
        lengthsHourlyForYear = lengthsHourlyByYear.loc[year]
        print(f"lenthsHourlyForYear:\n{lengthsHourlyForYear}")

        # Calculate numbers for polar histogram
        theta = np.linspace(0.0, 2 * np.pi, len(lengthsHourlyForYear), endpoint=False)
        radii = lengthsHourlyForYear
        width = (2*np.pi) / len(lengthsHourlyForYear)

        # Plot the data
        ax = plt.subplot(polar=True)
        ax.bar(theta, radii, color=yearColor["color"], width=width)

        # Formatting
        ax.set_xticks(theta, lengthsHourlyForYear.index, size=10, position=(0,-0.02))
        
        # Title
        ax.set_title(f"Message lengths by hour for {year}", loc="left")

        savePlot(f"message_lengths_clock_{year}")

def plotWords(messageTimesSplit, tkWindow, updateLabel):
    updateLabel("counting words")

    # Split via definition of "word" as any letters and apostrophes, and any dashes that are "sandwiched" between other letters
    words = messageTimesSplit["Contents"].map(lambda f: re.findall(r"(?:[a-zA-Z']|(?<=[a-zA-Z])-(?=[a-zA-Z]))+", str(f).lower())).explode()
    
    # Count number of words using that reasonable definition
    mostUsedWords = words.groupby(words).count().sort_values(ascending=False)

    # Add a "rank" column
    rankColumn = mostUsedWords.rank(method="max", ascending=False).astype(int)
    mostUsedWords = pd.concat([mostUsedWords.rename("Count"), rankColumn.rename("Rank")], axis=1)

    # Join with the version of the messages dataframe that has the message times formatted
    messageWords = pd.merge(words.rename("word"), messageTimesSplit, left_index=True, right_index=True)
    
    # Start visualizing this
    wordsBasicInfo(mostUsedWords["Count"].sum())
    updateLabel("most used words")
    wordRankings(words)
    updateLabel("word trends")
    wordTrends(messageWords, tkWindow)
def wordsBasicInfo(totalWords):
    fig, ax = plt.subplots()
    ax.set_axis_off()

    # Total messages
    ax.set_title(f"{totalWords} total words sent")
    
    # Retyping time calculations
    retypingTimeMinutes = totalWords/50
    retypingTimeHours = round(retypingTimeMinutes/60, 1 if retypingTimeMinutes<6000 else 0)
    retypingTimeComparison = ""
    if retypingTimeHours >= 40*52:
        retypingTimeComparison = f"{round(retypingTimeHours/(40*52), 1)} years of 40-hour workweeks"
    elif retypingTimeHours >= 40:
        retypingTimeComparison = f"{round(retypingTimeHours/40, 1)} 40-hour workweeks"
    
    # Printed weight
    pages = totalWords/250
    reams = pages/500
    pounds = round(reams*20, 1 if reams < 1 else 0)
    
    # Display the info
    info1 = ""
    if retypingTimeHours<40:
         info1 = f"If you consistently typed at 50 words per minute, it would take {retypingTimeHours} hours to retype your messages."
    else:
        info1 = f"If you consistently typed at 50 words per minute, it would take {retypingTimeHours} hours to retype your messages, which is equal to {retypingTimeComparison}."
    
    info2 = f"Based on the assumption that a non-double-sided page can fit 250 words, a printed copy of your messages would weigh {pounds} pounds."
    ax.text(0, 0.95, f"{info1}\n\n{info2}", horizontalalignment="left", verticalalignment="top", wrap=True)
    
    savePlot("messages_basic_info")
def wordRankings(words):
    # Get the rankings and usage count of words
    mostUsedWords = words.value_counts().sort_values(ascending=False)
    mostUsedWords = pd.concat([mostUsedWords.rename("Count"), mostUsedWords.rank(method="min", ascending=False).rename("Rank").astype(int)], axis=1)
    mostUsedWords.index = mostUsedWords.index.rename("")
    top500 = mostUsedWords.head(500).to_string()

    # Find where to save the file 
    rootFolder = os.path.dirname(__file__)
    txtPath = f"{rootFolder}/results/most_used_words.txt"

    # Save as a txt file
    output_file = open(txtPath, "w")
    output_file.write(top500)
    output_file.close()
    
def wordTrends(messageWords, tkWindow):
    # Get rid of the index of MessageWords so that it can be crosstabbed
    words = messageWords.reset_index()

    # Get the frequency of each word by month and year
    wordFreqs = pd.crosstab(index=words["word"], columns=[words["Timestamp"].dt.year.rename("year"), words["Timestamp"].dt.month.rename("month")])
        
    # Add rows for missing months
    wordFreqs = wordFreqs.reindex(pd.MultiIndex.from_product([wordFreqs.columns.get_level_values(0).unique(), np.arange(1, 13)]), axis=1, fill_value=0)        
    wordFreqs = wordFreqs.sort_index(key=lambda _: wordFreqs.sum(axis=1), ascending=False)

    # Figure out how many charts to make (25 words per chart, max 10 charts)
    numberOfCharts = min((len(wordFreqs.index) // 25), 10)
    
    # Display a progress bar for the charts
    chartProgress = ttk.Progressbar(tkWindow, length=300)
    chartProgress.grid()
    chartProgressLabel = ttk.Label(tkWindow, text="Starting charting words")
    chartProgressLabel.grid()
    
    # Create the charts
    for startIndex in range(0, numberOfCharts*25, 25):
        fig,axs = plt.subplots(5, 5, figsize=(15, 15))
        
        # Create a 5x5 grid of word charts
        i = 0
        print("Making subplots")
        for row in axs:
            for ax in row:
                # Create a chart for one word
                wordRank = startIndex + i
                wordFreqSlice = wordFreqs.iloc[wordRank]
                word = wordFreqSlice.name
                
                # Make a scatterplot
                ax.plot(list(wordFreqSlice))
                ax.set_title(f"{word} (#{wordRank + 1})")
                
                # Create a list of the first value of every month
                monthsToShow = wordFreqSlice.index.get_level_values(0).unique().map(lambda g: f"1/{str(g)[-2:]}")
                monthPlotIndexes = range(0, len(monthsToShow)*12, 12)                
                
                ax.set_xticks(monthPlotIndexes, monthsToShow)
                ax.spines[["top","right"]].set_visible(False)
                i += 1

                # Update progress UI
                # "Plotting top XX words (subplot X of X)..."
                chartProgressLabel.config(text=f"Plotting top {startIndex+25} words (subplot {i} of {25})...")
                pctProgress = i/25
                chartProgress["value"]=pctProgress*100

        # Update progress UI
        chartProgressLabel.config(text=f"Plotting top {startIndex+1} to {startIndex+25} words (saving plot)...")
        
        # Title
        fig.suptitle(f"Word usages by month (top {startIndex+1} to {startIndex+25})", horizontalalignment="center", size=32)

        # Save the charts
        print("Saving plot")
        fig.tight_layout()
        savePlot(f"messages_top_{startIndex+25}", 75)
    
    # Remove the progress bar
    chartProgress.grid_forget()
    chartProgressLabel.grid_forget()

def openFileExplorer(processLabel):
    rootFolder = os.path.dirname(__file__)
    exportPath = f"{rootFolder}\\results"
    
    if (os.name in ['nt', 'ce']):
        print("Opening file explorer")
        os.startfile(os.path.normpath(exportPath))
    
    processLabel.config(text=f"Data analysis finished! You can view your results at {exportPath}.")