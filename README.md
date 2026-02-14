# accessibility-software

Before running:
1. Install Python and pip (package installer) if not already installed.
2. Install the required dependencies by running the following command in your terminal:
```
pip install pyautogui keyboard mss Pillow pyttsx3 anthropic
```

Then, the software can be run with:
```
python main.py
```

main.py does not contain an Anthropic API key. Either use the one provided on line 25 of the PDF submitted to the regional conference or generate your own, then add it to line 25:
```
api_key="API-KEY"
```
