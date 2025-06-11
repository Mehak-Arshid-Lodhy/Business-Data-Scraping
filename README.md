# Business-Data-Scraping
This Python script is designed to scrape business details such as name, location, team members, emails, and phone numbers from Google and LinkedIn based on input criteria (business category and location).

# 📊 Business Data Scraping and Details

This Python script is designed to scrape business details such as **name**, **location**, **team members**, **emails**, and **phone numbers** from **Google** and **LinkedIn**, based on user-defined input like business category and location. It combines API access, Selenium-based web scraping, and Gemini LLM-powered manual input processing to generate structured business data in both CSV and JSON formats.

---

## 🎯 Objective

To automate the collection of business contact data using scraping and AI tools, especially when APIs or scraping access is limited or restricted.

---

## 🚀 Features

### ✅ Input Parameters
- **Business Category** – e.g., `Digital Marketing Agencies`
- **Location** – e.g., `Abbottabad, Pakistan`
- **Fallback Location** – Used when the primary location yields no results

### 🌐 Google Data Collection
- **Google Places API** (optional, currently mocked by Gemini API)
- **Selenium-based scraping** for public Google Search results
- **Manual input support** – prompts the user to input raw search results, which are processed using the **Gemini API**

### 👥 LinkedIn Data Collection
- Manual input only (employee names, job titles, emails)
- Processed using Gemini for formatting and extraction

### 🧹 Data Cleaning & Export
- Deduplication and relevance filtering
- Output files:
  - `business_data.csv`
  - `business_data.json`

### 🔐 Ethical Compliance
- User-agent rotation via `fake_useragent`
- Proxy support for anonymous access
- Limits scraping to 5 businesses per query for responsible data collection

### ⏰ Automation
- Scheduled scraping (e.g., every day at 08:00 AM) using `schedule` module

---

## 📂 Output Files Description

| File Name                                | Description                                                              |
|-----------------------------------------|--------------------------------------------------------------------------|
| `business_data.csv`                     | Cleaned business data in CSV format                                      |
| `business_data.json`                    | Structured JSON format of the same data                                  |
| `captcha_page_selenium_<query>.html`    | CAPTCHA pages saved during Selenium scraping for debugging               |
| `captcha_page_requests_<query>.html`    | CAPTCHA pages from requests-based scraping (fallback method)             |
| `final_google_page.html`                | Saved HTML page when all scraping methods fail (for diagnostics)         |

---

## ⚠️ Current Limitations

1. **Google Places API** is not integrated due to cost; data is generated using **Gemini API**, which may return mock data.
2. **CAPTCHA barriers** from Google and LinkedIn can prevent full automation; no CAPTCHA-solving system is in place yet.
3. **LinkedIn scraping** is manual due to restrictions on automated access.
4. **Data Accuracy** may vary, especially when using Gemini-generated mock data instead of live sources.

---

## 🔄 Workarounds & Enhancements

- **Selenium Fallback**: Mimics human interaction on Google Search to bypass some scraping restrictions
- **Gemini API Processing**: Converts raw/manual input into structured formats
- **User-Agent Rotation & Proxies**: Helps reduce the risk of blocking or banning
- **Data Cleaning Module**: Ensures unique and relevant records are retained

---

## 🔮 Future Improvements

- Integrate official **Google Places API** for high-accuracy results
- Add support for **CAPTCHA-solving services** (e.g., 2Captcha or Anti-Captcha)
- Use **LinkedIn People API** for automated employee data retrieval
- Strengthen validation for fake/malformed records

---

## 💡 How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Mehak-Arshid-Lodhy/business-data-scraping.git
   cd business-data-scraping
