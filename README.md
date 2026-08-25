# Tesseras Creare

## Description

Tesseras Creare: "to create passwords" <br>

This is a simple wordlist generator written in pure python. It takes some words and generates candidates based on various common patterns of passwords. <br>


## Installation

You can install this tool with pipx:

```
git clone https://github.com/CanOzSec/tesseras-creare
cd tesseras-creare && pipx install .
```

Or simply give it an alias in your `.bashrc`:

```
alias tesseras-creare='python3 /path/to/tesseras-creare/tesseras_creare/__main__.py'
```

## Usage

Input words from cli:
```
tesseras-creare -w test,company,petname,etc
```

Input words from file:
```
tesseras-creare -w small-newlined-wordlist.txt
```

## Tips

It is not recommended to provide this tool with huge wordlists as input, since it tries to create as many combinations as possible from a small number of words.

You can create or edit patterns easily in `__main__.py`.
