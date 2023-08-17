import sqlite3
import re

# Connects to the wordleWords database
connection = sqlite3.connect("wordleWords.db")
cursor = connection.cursor()

# Prints a random starting word for the user to try
result = cursor.execute("SELECT word FROM words ORDER BY RANDOM()")
potentialWords = [x[0] for x in result.fetchall()]
lastWordTried = potentialWords.pop(0)
print("\nRandom starting word - " + lastWordTried)

# Makes lists to track what letters can't be, letters that occur somewhere, and confirmed letters
lettersAreNot = [[],[],[],[],[]]
lettersSomeWhere = []
confirmedLetters = [0,0,0,0,0]

# Repeats steps 5 times until the wordle is solved or attempts run out
for i in range(5):
    # Gets the result from the user and checks if it is a valid input
    while True:
        wordleResult = input("Enter a 0 for wrong character, 1 for wrong place right character, and 2 for correct character. Example - 00122.\nEnter 'Another' for a differnet word to try: ")
        # User can request a different word, mainly used when testing the program on other wordle sites as their word lists are smaller than the official wordle list
        if wordleResult.lower() == "another":
            lastWordTried = potentialWords.pop(0)
            print("\nNext word to try - " + lastWordTried)
            continue
        if re.search("^[0-2]{5}$",wordleResult) != None:
            break
        else:
            print("\nThat's not a valid option, please try again.")

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

    # Picks a random word from all the possible words given the previous conditions
    result = cursor.execute("SELECT word FROM words WHERE " + whereConditions + "ORDER BY RANDOM()")
    potentialWords = [x[0] for x in result.fetchall()]
    if len(potentialWords) > 0:
        lastWordTried = potentialWords.pop(0)
    else:
        print("There are no words that meet the requirements.")
        break
    print("\nNext word to try - " + lastWordTried)