import sqlite3
import requests
import string

def makeDB():
    # Sets the working directory and makes the database
    connection = sqlite3.connect("wordleWords.db")
    cursor = connection.cursor()
    result = cursor.execute("CREATE TABLE words(word, letter1, letter2, letter3, letter4, letter5, score)")

    # Gets all the wordle words, reads it as a string, then splits it into a list
    response = requests.get("https://raw.githubusercontent.com/tabatkins/wordle-list/main/words")
    wordleWords = response.text
    wordleWordsList = wordleWords.split()

    # Makes dictionaries for each letter and the total to count character occurances
    letterCounts = [dict.fromkeys(string.ascii_lowercase, 0),dict.fromkeys(string.ascii_lowercase, 0),dict.fromkeys(string.ascii_lowercase, 0),dict.fromkeys(string.ascii_lowercase, 0),dict.fromkeys(string.ascii_lowercase, 0)]
    for i in wordleWordsList:
        for j in range(5):
            letterCounts[j][i[j]] += 1

    # Calculates the averages fro each character in each letter position
    words = len(wordleWordsList)
    for i in letterCounts:
        for j in i:
            i[j] = round((i[j]/(words))*100,2)

    # Makes wordleWordList a tuple with the first element as the word and the second element of the average of it's letters frequency
    for i in range(len(wordleWordsList)):
        wordleWordsList[i] = (wordleWordsList[i], (letterCounts[0][wordleWordsList[i][0]] + letterCounts[1][wordleWordsList[i][1]] + letterCounts[2][wordleWordsList[i][2]] + letterCounts[3][wordleWordsList[i][3]] + letterCounts[4][wordleWordsList[i][4]])/5)

    # Adds all the words from the wordleWordsList into the database
    for i in wordleWordsList:
        cursor.execute("INSERT INTO words VALUES ('" + i[0] + "', '" + i[0][0] +"', '" + i[0][1] +"', '" + i[0][2] +"', '" + i[0][3] +"', '" + i[0][4] +"', " + str(i[1]) + ")")

    connection.commit()