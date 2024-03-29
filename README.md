# Screenshot GPT
Screenshot GPT is an open-source Python GUI application built using the customtkinter library. It captures screenshots, extracts text, sends it to the OpenAI API, and displays the generated responses.

## Screenshots
<img src="screenshots/options.png" alt="Options" width="400"/>
<img src="screenshots/results.png" alt="Results" width="400"/>

## Features
* Supports custom left, upper, right, and lower crop coordinates
* Choose between different GPT-4 and GPT-3.5 text models
* Input and manage your API key for accessing the AI models
* View detailed results with images, extracted texts, and responses

## Dependencies
* customtkinter
* tkinter
* tkinter.messagebox
* pyautogui
* pillow
* easyocr
* openai
  
## Installation
**1. Clone the repository**
```bash
git clone https://github.com/PouyaMT/screenshot-gpt.git
```

**2. Install the dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the script**
```bash
python main.py
```
