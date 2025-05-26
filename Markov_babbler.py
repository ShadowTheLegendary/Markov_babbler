import os
import random
import json

def is_end(word):
    return word[-1] in ['.', '!', '?']

def get_stats(text="And this and that."):
    processed_words = text.split()
    stats = {}

    for i in range(len(processed_words) - 1):
        stats.setdefault(processed_words[i], []).append(processed_words[i + 1])

    return stats

def add_to_stats(stats, text=""):
    processed_words = text.split()

    for i in range(len(processed_words) - 1):
        stats.setdefault(processed_words[i], []).append(processed_words[i + 1])

    return stats

def babble(stats, sentences):
    result = ""
    for _ in range(sentences):
        try:
            word = random.choice(list(stats.keys()))
            sentence = word.capitalize()
            while not is_end(word):
                word = random.choice(stats[word])
                sentence += " " + word
            result += sentence + " "
        except (KeyError, IndexError):
            continue
    return result.strip()

def user_interface():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("Welcome to the Markov babbler!")

        filepath = input("What file do you want to train the model on (without .txt): ").strip()
        full_path = f"{filepath}.txt"

        if not os.path.exists(full_path):
            print(f"❌ File not found: {full_path}")
            choice = input("Type 'quit' to exit or press Enter to try again: ").strip().lower()
            if choice == "quit":
                return
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as file:
                text = file.read()
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            input("Press Enter to try again...")
            continue

        stats = get_stats(text)

        while True:
            try:
                sentences = int(input("How many sentences of babble do you want: "))
                if sentences <= 0:
                    raise ValueError("Must be a positive integer.")
                break
            except ValueError as ve:
                print(f"❌ Invalid input: {ve}")

        print("\nGenerated Babble:\n")
        print(babble(stats, sentences))
        print("\n---")

        choice = input("Type 'quit' to exit or press Enter to continue: ").strip().lower()
        if choice == "quit":
            return

# To enable this CLI, uncomment below:
# if __name__ == "__main__":
#     user_interface()
