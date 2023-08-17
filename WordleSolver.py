import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from python_imagesearch.imagesearch import *
import time
from PIL import ImageGrab

# Connects to the wordleWords database
connection = sqlite3.connect("wordleWords.db")
cursor = connection.cursor()

# Opens the wordle webpage in chrome
wordleURL = 'https://www.nytimes.com/games/wordle/index.html'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument("--incognito")
chromeOptions.add_experimental_option("detach", True)
browser = webdriver.Chrome(options=chromeOptions)
browser.get(wordleURL)
timeWaited = 0 # In case this popup is removed in the future, this ensures the code doesn't get in loop

# Closes a window about wordle's updated terms and conditions
position = imagesearch("./WordleContinueButton.png")
while position == [-1,-1] and timeWaited < 5:  # Gives some extra time for page to load
    time.sleep(.1) # Time between checks
    timeWaited += .1
    position = imagesearch("./WordlePlayButton.png") # Looks for image on screen and updates position, returns [-1,-1] if not found
pyautogui.click(position[0]+15, position[1]+15)

timeWaited = 0
# Finds the next popup and closes it
position = imagesearch("./WordlePlayButton.png")
while position == [-1,-1] and timeWaited < 5:
    time.sleep(.1)
    position = imagesearch("./WordlePlayButton.png")
pyautogui.click(position[0]+15, position[1]+15)

# Presses esc to close the final popup
time.sleep(.5)
pyautogui.press('esc')

# Finds the wordle board
position = imagesearch("./WordleBoard.png")
while position == [-1,-1]:
    time.sleep(.1)
    position = imagesearch("./WordleBoard.png")

# Picks a word from all the possible words based on its character score
result = cursor.execute("SELECT word FROM words ORDER BY score DESC")
potentialWords = [x[0] for x in result.fetchall()]
lastWordTried = potentialWords.pop(0)
print("\nRandom starting word - " + lastWordTried)

# Makes lists to track what letters can't be, letters that occur somewhere, and confirmed letters
lettersAreNot = [[],[],[],[],[]]
lettersSomeWhere = []
confirmedLetters = [0,0,0,0,0]

# Types the first word in the chat and then enters it
pyautogui.write(lastWordTried, interval=0.25)
pyautogui.press('enter')

# Makes a list of offsets
xPositionOffset = [15,82,149,216,283]
yPositionOffset = [15,85,152,219,286]

# Yellow RGB (181, 159, 59)
# Gray RGB (58, 58, 60)
# Green RGB (83, 141, 78)

# Repeats steps 5 times until the wordle is solved or attempts run out
for i in range(5):
    # Gets the results from the last word entered
    wordleResult = ""
    time.sleep(2)
    for j in range(5):
        r,g,b = ImageGrab.grab(bbox=(position[0]+xPositionOffset[j], position[1]+xPositionOffset[i], position[0]+xPositionOffset[j]+1, position[1]+xPositionOffset[i]+1)).convert('RGB').getpixel((0,0))
        if r == 181:
            wordleResult += "1"
        elif r == 83:
            wordleResult += "2"
        else:
            wordleResult += "0"
    
    print(wordleResult)

    # Handles if lastWordTried is correct
    if wordleResult == "22222":
        print("The wordle has been solved!")
        break

    # Parses through wordleResult and adds the letters to the appropriate lists
    for i in range(len(wordleResult)):
        # If letter is in word but not that spot
        if wordleResult[i] == "1":
            lettersAreNot[i].append(lastWordTried[i])
            if lastWordTried[i] not in lettersSomeWhere:
                lettersSomeWhere.append(lastWordTried[i])
        
        # If letter is in the right spot, it is added to confirmedLetters and if it was in lettersSomewhere, it is removed
        if wordleResult[i] == "2":
            confirmedLetters[i] = lastWordTried[i]
            if lastWordTried[i] in lettersSomeWhere:
                lettersSomeWhere.remove(lastWordTried[i])
        
    # Handled after the other two so that letters are only added to every lettersAreNot if they don't appear in lettersSomewhere
    for i in range(len(wordleResult)):
        # If letter isn't in word then it is added to every list in lettersAreNot
        if wordleResult[i] == "0":
            if lastWordTried[i] not in lettersSomeWhere:
                for j in range(len(lettersAreNot)):
                    lettersAreNot[j].append(lastWordTried[i])
            else:
                lettersAreNot[i].append(lastWordTried[i])

    # Gets a list of next possible words for the next guess by looking through words with conditions from lettersAreNot, lettersSomewhere, and confirmedLetters
    whereConditions = ""
    openLetters = []
    for i in range(5):
        if i > 0: whereConditions += " AND "
        if confirmedLetters[i] != 0:
            whereConditions += "letter" + str(i+1) + " = '" + confirmedLetters[i] + "'"
        else:
            openLetters.append("letter" + str(i+1))
            listString = "("
            for j in lettersAreNot[i]:
                listString += "'" + j + "',"
            listString = listString[:len(listString)-1] + ")"
            whereConditions += "letter" + str(i+1) + " NOT IN " + listString
    
    # Narrows it down to words that have the letters somewhere in the word in one of the open letter places
    for i in lettersSomeWhere:
        whereConditions += " AND '" + i + "' IN "
        listString = "("
        for j in openLetters:
            listString += j + ","
        listString = listString[:len(listString)-1] + ")"
        whereConditions += listString

    # Picks a word from all the possible words given the previous conditions based on its character score
    result = cursor.execute("SELECT word FROM words WHERE " + whereConditions + "ORDER BY score DESC")
    potentialWords = [x[0] for x in result.fetchall()]
    if len(potentialWords) > 0:
        lastWordTried = potentialWords.pop(0)
    else:
        print("There are no words that meet the requirements.")
        break
    print("\nNext word to try - " + lastWordTried)

    # Types the first word in the chat and then enters it
    pyautogui.write(lastWordTried, interval=0.25)
    pyautogui.press('enter')