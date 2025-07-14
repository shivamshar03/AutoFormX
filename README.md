# 🤖 AutoFormX — Smart Web Form Filler with CSV Input

**AutoFormX** is a powerful automation tool that uses **Selenium**, **BeautifulSoup**, and **RapidFuzz** to intelligently fill and submit online forms using data from a CSV file. It supports modern, dynamic form elements including checkboxes, dropdowns, and more — even in React-based UIs.

---

## 🚀 Features

- 📄 Fills online forms using a CSV file
- 🔍 Fuzzy matching to align CSV columns with form fields
- 🧠 Handles:
  - Text inputs
  - Emails and URLs
  - React-style checkboxes
  - Native dropdowns (`<select>`)
- 🔁 Retry mechanism for failed submissions
- 📸 Screenshots captured for errors
- 🔧 Configurable and extendable

---

## 📂 Folder Structure

```
📦 AutoFormX/
┣ 📄 form_data.csv
┣ 📄 form_filler.py
┣ 📂 error_screenshots/
┗ 📄 README.md
```


---

## 📥 Requirements

- Python 3.7+
- Google Chrome + ChromeDriver
- Install dependencies:

```bash
pip install selenium pandas beautifulsoup4 rapidfuzz
```

## 📄 Input File: form_data.csv
Your CSV file should look like this:
```
Name,Email,Skills,ProjectIdea,Availability,PortfolioURL,AdditionalDetails
Shivam Sharma,shivam@example.com,"AI/ML,Frontend Development",An AI assistant,flexible,https://github.com/shivamshar03,Looking for ML collaborators.
```

## ✅ Notes:
Availability must exactly match one of the form's <option value=""> values:
```
full-time, part-time, weekends, flexible
```
Skills can be comma-separated

## ⚙️ Configuration
Edit these in form_filler.py to customize:
```
CSV_PATH = "form_data.csv"
FORM_URL = "https://shivam-sharma.vercel.app/collaborate"
MAX_RETRIES = 1
HEADLESS = False
Set HEADLESS = True to run the browser invisibly in the background.
```

## 🧠 How AutoFormX Works
- Scrapes the form structure using BeautifulSoup. 
- Matches field labels/placeholders to CSV headers with RapidFuzz.
- Inputs values via Selenium.
- Clicks React-based checkboxes and buttons using JavaScript.
- Submits the form and waits for confirmation.

## 📸 Screenshots on Error
If something goes wrong during a submission, a screenshot is saved to:

```
/error_screenshots/error_row_<index>.png
```

## 📌 Tech Stack
```
Selenium
BeautifulSoup
RapidFuzz
pandas
```
## 👤 Author
Shivam Sharma
🌐 Portfolio
🐙 GitHub

## 📬 Contributing
Want to improve field matching, add file uploads, or support Google Sheets?
Feel free to fork and open a PR!

## 📜 License
This project is open-source and free to use under the MIT License.

### ✨ AutoFormX — Fill smarter. Submit faster.
