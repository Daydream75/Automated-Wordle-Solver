import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pyautogui

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

# Closes the three popups that appear
# They are inside try-except so that if these elements are later removed from the wordle site it doesn't break this code
# If they are later changed then this might will need updated as they might not be found/closed properly
try:
    continueButton = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//BUTTON[@Class='purr-blocker-card__button']")))
    continueButton.click()
except TimeoutException:
    pass

try:
    playButton = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='Play']")))
    playButton.click()
except TimeoutException:
    pass

try:
    xButton = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@aria-label='Close']")))
    xButton.click()
except TimeoutException:
    pass

# Picks a word from all the possible words based on its character score
result = cursor.execute("SELECT word FROM words ORDER BY score DESC")
potentialWords = [x[0] for x in result.fetchall()]
lastWordTried = potentialWords.pop(0)
print("\nStarting word - " + lastWordTried)

# Makes lists to track what letters can't be, letters that occur somewhere, and confirmed letters
lettersAreNot = [[],[],[],[],[]]
lettersSomeWhere = []
confirmedLetters = [0,0,0,0,0]

# Types the first word in the chat and then enters it
time.sleep(1)
pyautogui.write(lastWordTried, interval=.05)
pyautogui.press('enter')

# Repeats steps 5 times until the wordle is solved or attempts run out
for i in range(5):

    # Gets the results from the last word entered
    wordleResult = ""
    for j in range(5):
        status = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@aria-label='Row " + str(i+1) + "']/descendant::div[@style='animation-delay: " + str(j * 100) + "ms;']/descendant::div[@class='Tile-module_tile__UWEHN']"))).get_attribute("data-state")
        while status == "tbd":
            time.sleep(.1)
            status = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@aria-label='Row " + str(i+1) + "']/descendant::div[@style='animation-delay: " + str(j * 100) + "ms;']/descendant::div[@class='Tile-module_tile__UWEHN']"))).get_attribute("data-state")
        if status == "absent": wordleResult += "0"
        elif status == "present": wordleResult += "1"
        else: wordleResult += "2"

    # Handles if lastWordTried is correct
    if wordleResult == "22222":
        print("The wordle has been solved!")
        break

    # Parses through wordleResult and adds the letters to the appropriate lists
    for i in range(len(wordleResult.lower())):
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
    time.sleep(.5)
    pyautogui.write(lastWordTried, interval=0.25)
    pyautogui.press('enter')