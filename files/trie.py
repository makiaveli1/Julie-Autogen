from collections import defaultdict


language_keywords = {
    "python": ["def", "import", "print", "return", "class"],
    "javascript": ["function", "var", "let", "const", "return"],
    "html": ["<html>", "<head>", "<body>", "<div>", "<p>"],
    "shell": ["echo", "ls", "cd", "mkdir", "rm"],
    "bash": ["#!/bin/bash", "echo", "ls", "cd", "mkdir"],
    "applescript": ["tell", "end tell", "run", "set", "get"],
    "r": ["<-", "function", "print", "return", "library"]
}

# Trie Node class
class TrieNode:
    def __init__(self):
        self.children = defaultdict()
        self.is_end_of_word = False

# Trie class
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, text):
        count = 0
        node = self.root
        for char in text:
            if char in node.children:
                node = node.children[char]
                if node.is_end_of_word:
                    count += 1
                    node = self.root
            else:
                node = self.root
        return count
