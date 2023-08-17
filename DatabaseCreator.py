import sqlite3
import os
import requests

# Sets the working directory and makes the database
connection = sqlite3.connect("wordleWords.db")
cursor = connection.cursor()
result = cursor.execute("CREATE TABLE words(word, letter1, letter2, letter3, letter4, letter5)")

# Gets all the wordle words, reads it as a string, then splits it into a list
response = requests.get("https://raw.githubusercontent.com/tabatkins/wordle-list/main/words")
wordleWords = response.text
wordleWordsList = wordleWords.split()

# Adds all the words from the wordleWordsList into the database
for i in wordleWordsList:
    cursor.execute("INSERT INTO words VALUES ('" + i + "', '" + i[0] +"', '" + i[1] +"', '" + i[2] +"', '" + i[3] +"', '" + i[4] +"')")

connection.commit()