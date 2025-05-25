import os
import random
import json

def is_end(word):
    if word[-1] in ['.', '!', '?']:
        return True
    return False

def get_stats(str = "And this and that."):
    procesed_words = str.split()
    stats = {}
    
    for i in range(len(procesed_words) - 1):
        if procesed_words[i] in stats.keys():
            stats[procesed_words[i]].append(procesed_words[i+1])
        else:
            stats[procesed_words[i]] = [procesed_words[i+1]]
    return stats

def add_to_stats(stats, str = ""):
    procesed_words = str.split()
    
    for i in range(len(procesed_words) - 1):
        if procesed_words[i] in stats.keys():
            stats[procesed_words[i]].append(procesed_words[i+1])
        else:
            stats[procesed_words[i]] = [procesed_words[i+1]]
    return stats

def babble(stats, sentances):
    result = ""
    for i in range(sentances):
        word = random.choice(list(stats.keys()))
        sentance = word.capitalize()
        while not is_end(word):
            word = random.choice(stats[word])
            sentance += " " + word
        result += sentance + " "
    return result

def user_interface():
    while True:
        os.system("cls")
        print("Welcome to the Markov babbler!")
        filepath = input("What file do you want to train the model on: ")
        try:
            file = open(filepath + ".txt", "r", encoding="utf-8")
            text = file.read()
            file.close()
        except:
            print(f"I cant find: {filepath}.txt")
            choice = input()
            if choice == "quit":
                return
            continue
        stats = get_stats(text)
        sentances = input("How many sentances of babble do you want: ")
        print(babble(stats, int(sentances)))
        choice = input()
        if choice == "quit":
            return

#if __name__ == "__main__":
 #   user_interface()