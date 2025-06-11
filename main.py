# main.py
# This program collects information about digital marketing agencies in Abbottabad, Pakistan.
# It gathers business details like name, address, website, and phone number from Google, and team member
# details like name, job title, and email from LinkedIn. It uses Google’s Places API for reliable data
# collection, with Selenium as a backup if the API fails. LinkedIn data is entered manually because
# automated scraping is restricted. The data is saved in CSV and JSON files, following ethical guidelines
# and supporting scheduled runs. The code is designed to work in Visual Studio Code on Windows and meets
# Task 2 requirements by June 10, 2025.

# Import statements bring in external tools (libraries) needed for the program.
import googlemaps  # This library lets us use Google Maps API to get business details, like finding places on a map.
import requests  # This library helps us fetch web pages by sending HTTP requests, like visiting a website.
from bs4 import BeautifulSoup  # BeautifulSoup helps us read and extract information from HTML web pages, like picking out specific text.
import pandas as pd  # Pandas organizes data into tables (like Excel) and saves it to CSV files.
from selenium import webdriver  # Selenium controls a web browser automatically, like opening Chrome and clicking links.
from selenium.webdriver.chrome.options import Options  # This provides settings to customize how Chrome behaves in Selenium.
from selenium.webdriver.chrome.service import Service  # This manages the ChromeDriver, a tool Selenium uses to control Chrome.
from webdriver_manager.chrome import ChromeDriverManager  # This automatically downloads and sets up ChromeDriver for Selenium.
from fake_useragent import UserAgent  # This creates random user-agents to make our browser look like a real person’s browser.
import time  # This library lets us add pauses (delays) to avoid overloading websites.
import json  # JSON is a format for storing data; this library helps us read and write JSON files.
import re  # This library helps us find patterns in text, like phone numbers or specific words.
import random  # This library generates random numbers, used for random delays to mimic human behavior.
from datetime import datetime  # This library handles dates and times, useful for scheduling or logging.
import schedule  # This library schedules tasks, like running the program every day at a specific time.
import google.generativeai as genai  # Google’s Gemini AI helps process text into structured data, like turning raw text into a list of businesses.
import os  # This library interacts with the operating system, like creating or saving files.
import logging  # This library logs messages (like errors or progress) to help debug the program.

# These lines reduce extra messages (warnings) from Selenium and TensorFlow to keep the output clean.
logging.getLogger('selenium').setLevel(logging.WARNING)  # Sets Selenium to only show important messages, ignoring minor warnings.
logging.getLogger('tensorflow').setLevel(logging.ERROR)  # Sets TensorFlow to only show errors, ignoring other warnings.

# Configuration settings define key values used throughout the program, like constants.
BUSINESS_CATEGORY = "digital marketing agencies"  # The type of businesses we’re searching for (digital marketing agencies).
LOCATION = "Abbottabad, Pakistan"  # The main city we’re searching in for businesses.
FALLBACK_LOCATION = "Khyber Pakhtunkhwa, Pakistan"  # A backup location to try if the main city gives no results.
OUTPUT_FILE = "business_data.csv"  # The name of the CSV file where we’ll save the results.
GOOGLE_API_KEY = "AIzaSyCQEupJ6uDBDtDLL-iSwTc9uJZvuT5_OuE"  # The key to access Google Maps API (get this from Google Cloud Console).
GEMINI_API_KEY = "AIzaSyCQEupJ6uDBDtDLL-iSwTc9uJZvuT5_OuE"  # The key to access Gemini AI (get this from Google AI Studio).
PROXY = None  # A proxy server for web requests (None means no proxy; can add one like 'http://user:pass@host:port' for anonymity).
SCHEDULE_ENABLED = False  # Set to True to run the program daily; False means it runs only once when started.

# Initialize the Google Maps client to connect to Google’s API for searching businesses.
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)  # Creates a connection to Google Maps using the API key; 'googlemaps.Client' is a class that handles API requests.

# Configure the Gemini AI API to process text data.
genai.configure(api_key=GEMINI_API_KEY)  # Sets up the Gemini AI with the API key; 'genai.configure' prepares the API for use.

# Function to set up Selenium WebDriver, which controls a Chrome browser for web scraping.
def setup_driver():
    """This function sets up a Chrome browser using Selenium to scrape websites. It uses settings to avoid detection by websites."""
    ua = UserAgent()  # Creates a UserAgent object to generate random user-agents, making the browser look like a real user.
    chrome_options = Options()  # Creates an Options object to set up Chrome’s behavior; 'Options' is a Selenium class for browser settings.
    # The next line is commented out; it would make Chrome run without a visible window (headless mode), useful for production.
    # chrome_options.add_argument('--headless')  # If uncommented, Chrome runs invisibly; currently disabled for debugging CAPTCHAs.
    chrome_options.add_argument('--no-sandbox')  # Disables sandboxing to improve stability on some systems; a sandbox limits browser actions for security.
    chrome_options.add_argument('--disable-dev-shm-usage')  # Reduces memory issues by disabling shared memory; helps on low-memory systems.
    chrome_options.add_argument('--disable-gpu')  # Disables GPU acceleration for better compatibility, as GPUs can cause issues in some setups.
    chrome_options.add_argument(f'user-agent={ua.random}')  # Sets a random user-agent; 'f' string formats the user-agent into the argument.
    chrome_options.add_argument('--log-level=3')  # Reduces Chrome’s log messages to errors only, keeping output clean.
    chrome_options.add_argument('--window-size=1280,720')  # Sets the browser window size to 1280x720 pixels for consistent rendering.
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # Hides automation signals to avoid detection by websites.
    chrome_options.add_experimental_option('useAutomationExtension', False)  # Disables Selenium’s automation extension to further avoid detection.
    if PROXY:  # 'if' checks if PROXY is not None; used to decide if a proxy server should be used.
        chrome_options.add_argument(f'--proxy-server={PROXY}')  # Sets the proxy server for browser requests if PROXY is provided.
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)  # Starts Chrome; 'ChromeDriverManager().install()' downloads ChromeDriver, 'Service' manages it, and 'webdriver.Chrome' opens the browser.
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {  # Runs JavaScript to hide Selenium’s 'webdriver' property, preventing websites from detecting automation.
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })  # This JavaScript code changes the browser’s properties to look less like a bot.
    return driver  # 'return' sends the driver object back to the caller so it can be used to control the browser.

# Function to scrape business details using Google Places API, which is a reliable way to get data.
def scrape_google_places(category, location):
    """This function uses Google’s Places API to find business details like name, address, website, and phone number for a given category and location."""
    try:  # 'try' starts a block to catch errors so the program doesn’t crash if something goes wrong.
        # Search for businesses using the category (e.g., "digital marketing agencies") and location (e.g., "Abbottabad, Pakistan").
        places = gmaps.places(f"{category} in {location}", type="business")  # Sends a search query to Google Places API; 'f' string combines category and location.
        businesses = []  # Creates an empty list to store business details; a list is like a collection of items in Python.
        
        for place in places.get('results', [])[:5]:  # 'for' loop goes through the top 5 results (limited for ethical reasons); 'get' safely retrieves 'results' or an empty list if none.
            place_id = place.get('place_id')  # Gets the unique ID for a place; 'get' retrieves the 'place_id' key from the place dictionary.
            details = gmaps.place(place_id=place_id, fields=['name', 'formatted_address', 'website', 'formatted_phone_number'])  # Fetches detailed info using the place ID; 'fields' specifies what data we want.
            result = details.get('result', {})  # Gets the result dictionary or an empty dictionary if none; 'get' avoids errors if 'result' is missing.
            businesses.append({  # 'append' adds a new dictionary to the businesses list; a dictionary stores key-value pairs like 'name': 'Business Name'.
                'name': result.get('name', 'N/A'),  # Gets the business name or 'N/A' if missing.
                'address': result.get('formatted_address', 'N/A'),  # Gets the address or 'N/A' if missing.
                'website': result.get('website', 'N/A'),  # Gets the website URL or 'N/A' if missing.
                'phone': result.get('formatted_phone_number', 'N/A'),  # Gets the phone number or 'N/A' if missing.
                'location': location,  # Adds the search location (e.g., "Abbottabad, Pakistan") to the data.
                'source': 'Google Places API'  # Notes that this data came from Google Places API.
            })  # This creates a dictionary for each business and adds it to the list.
        
        print(f"Retrieved {len(businesses)} businesses from Google Places API for query: {category} in {location}")  # Prints how many businesses were found; 'len' counts items in the list, 'f' string formats the message.
        return businesses  # Returns the list of businesses to the caller.
    except Exception as e:  # 'except' catches any errors; 'Exception' is a general error type, 'as e' stores the error message.
        print(f"Google Places API failed: {e}")  # Prints the error message to help debug.
        return []  # Returns an empty list if the API fails, so the program can continue.

# Commented-out code for solving CAPTCHAs with 2Captcha API (not active but included for reference).
#####IF I HAVE 2Captcha API key, I can use it to solve CAPTCHAs automatically.
# Note: If you have a 2Captcha API key, you can integrate it here to solve CAPTCHAs automatically.
# import base64  # Library to encode data, like images, into a format for 2Captcha.
# import requests  # Already imported above Jon to fetch CAPTCHA images or send data to 2Captcha.

# # Add your 2Captcha API key here
# CAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY"  # Placeholder for 2Captcha API key.

# def solve_captcha(image_url):
#     """This function would solve CAPTCHAs using the 2Captcha service."""
#     try:
#         # Send CAPTCHA image to 2Captcha
#         response = requests.post(
#             "http://2captcha.com/in.php",
#             data={
#                 "key": CAPTCHA_API_KEY,
#                 "method": "base64",
#                 "body": base64.b64encode(requests.get(image_url).content).decode(),
#                 "json": 1
#             }
#         )  # Sends the CAPTCHA image to 2Captcha for solving.
#         captcha_id = response.json().get("request")  # Gets the CAPTCHA ID from 2Captcha’s response.
#         if not captcha_id:
#             print("Failed to send CAPTCHA to 2Captcha.")
#             return None
#
#         # Wait for the solution
#         print("Waiting for CAPTCHA solution...")
#         while True:
#             solution_response = requests.get(
#                 f"http://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1"
#             )  # Checks if 2Captcha has solved the CAPTCHA.
#             solution = solution_response.json()  # Gets the solution response.
#             if solution.get("status") == 1:
#                 return solution.get("request")  # Returns the CAPTCHA solution.
#             time.sleep(5)  # Waits 5 seconds before checking again.
#     except Exception as e:
#         print(f"Error solving CAPTCHA: {e}")
#         return None

# def scrape_google_selenium(category, location, driver, max_retries=3):
#     """This function would scrape Google search results using Selenium and handle CAPTCHAs with 2Captcha."""
#     queries = [f"{category} in {location}", f"{category} in {FALLBACK_LOCATION}"]
#     raw_data = []
#
#     for query in queries:
#         url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
#         for attempt in range(max_retries):
#             try:
#                 driver.get(url)
#                 time.sleep(random.uniform(10, 15))
#
#                 # Scroll to load content
#                 for _ in range(random.randint(2, 4)):
#                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight * arguments[0]);", random.uniform(0.3, 0.7))
#                     time.sleep(random.uniform(1, 3))
#
#                 # Check for CAPTCHA
#                 if "captcha" in driver.page_source.lower() or "recaptcha" in driver.page_source.lower():
#                     print(f"CAPTCHA detected in Selenium for query '{query}'. Solving CAPTCHA...")
#                     captcha_image = driver.find_element_by_css_selector("img[src*='captcha']").get_attribute("src")
#                     captcha_solution = solve_captcha(captcha_image)
#                     if captcha_solution:
#                         driver.execute_script(f"document.getElementById('g-recaptcha-response').value='{captcha_solution}';")
#                         driver.find_element_by_id("captcha-form").submit()
#                         time.sleep(5)
#                         continue
#                     else:
#                         print("Failed to solve CAPTCHA.")
#                         break
#
#                 # Parse results
#                 soup = BeautifulSoup(driver.page_source, 'html.parser')
#                 results = soup.find_all('div', class_=re.compile('tF2Cxc|VwiC3b|yuRUbf|rllt__local|W4Efsd|rllt__details|section-result'))
#                 for result in results[:5]:
#                     text = result.get_text(separator=' ', strip=True)
#                     raw_data.append(text)
#
#                 print(f"Retrieved {len(raw_data)} raw results from Google (Selenium) for query: {query}")
#                 if raw_data:
#                     return raw_data
#             except Exception as e:
#                 print(f"Selenium attempt {attempt + 1} failed for query '{query}': {e}")
#                 if attempt < max_retries - 1:
#                     time.sleep(2 ** attempt)
#                 continue
#
#     print("Selenium scraping failed. Trying requests...")
#     return []

# Function to scrape Google search results using Selenium as a fallback if the Places API fails.
def scrape_google_selenium(category, location, driver, max_retries=3):
    """This function uses Selenium to control a Chrome browser and scrape Google search results when the Places API doesn’t work."""
    queries = [f"{category} in {location}", f"{category} in {FALLBACK_LOCATION}"]  # Creates a list of search queries for the primary and backup locations; a list holds multiple items.
    raw_data = []  # Creates an empty list to store raw text from search results.
    
    for query in queries:  # 'for' loop goes through each query in the list.
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"  # Creates a Google search URL; 'replace' changes spaces to '+' for valid URLs.
        for attempt in range(max_retries):  # 'for' loop tries up to max_retries times; 'range' generates numbers from 0 to max_retries-1.
            try:  # 'try' block catches errors to prevent crashes.
                driver.get(url)  # Loads the search URL in the Chrome browser; 'get' navigates to the page.
                time.sleep(random.uniform(10, 15))  # Pauses for 10-15 seconds (randomly chosen) to mimic human behavior; 'random.uniform' picks a random number.
                
                for _ in range(random.randint(2, 4)):  # Scrolls the page 2-4 times randomly; 'random.randint' picks a whole number.
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * arguments[0]);", random.uniform(0.3, 0.7))  # Scrolls partway down the page; 'execute_script' runs JavaScript.
                    time.sleep(random.uniform(1, 3))  # Waits 1-3 seconds after each scroll to let the page load.
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')  # Converts the page’s HTML to a BeautifulSoup object; 'page_source' gets the HTML, 'html.parser' is the parser type.
                if soup.find('div', id='captcha') or 'recaptcha' in driver.page_source.lower() or 'enablejs' in driver.page_source.lower():  # Checks for CAPTCHA; 'find' searches for a div with id 'captcha', 'lower' converts text to lowercase.
                    print(f"CAPTCHA detected in Selenium for query '{query}'. Saving HTML.")  # Prints a message if a CAPTCHA is found.
                    with open(f'captcha_page_selenium_{query.replace(" ", "_")}.html', 'w', encoding='utf-8') as f:  # Opens a file to save the HTML; 'with' ensures the file closes after writing.
                        f.write(driver.page_source)  # Writes the page’s HTML to a file for debugging.
                    break  # 'break' exits the attempt loop if a CAPTCHA is detected.
                
                results = soup.find_all('div', class_=re.compile('tF2Cxc|VwiC3b|yuRUbf|rllt__local|W4Efsd|rllt__details|section-result'))  # Finds search result divs; 'find_all' gets all matching elements, 're.compile' matches multiple class patterns.
                for result in results[:5]:  # Loops through the top 5 results to limit scraping.
                    text = result.get_text(separator=' ', strip=True)  # Gets text from each result; 'get_text' extracts text, 'separator' joins with spaces, 'strip' removes extra spaces.
                    raw_data.append(text)  # Adds the text to the raw_data list; 'append' adds an item to the end of the list.
                
                print(f"Retrieved {len(raw_data)} raw results from Google (Selenium) for query: {query}")  # Prints how many results were found.
                if raw_data:  # 'if' checks if raw_data is not empty.
                    return raw_data  # Returns the raw data if any was found.
            except Exception as e:  # Catches any errors during the attempt.
                print(f"Selenium attempt {attempt + 1} failed for query '{query}': {e}")  # Prints the error with the attempt number.
                if attempt < max_retries - 1:  # Checks if there are more attempts left.
                    time.sleep(2 ** attempt)  # Waits longer each retry (2, 4, 8 seconds); '**' is the power operator.
                continue  # 'continue' skips to the next attempt.
    
    print("Selenium scraping failed. Trying requests...")  # If Selenium fails, try another method.
    # Fallback to using the requests library for scraping.
    ua = UserAgent()  # Creates a new UserAgent object for a random user-agent.
    headers = {'User-Agent': ua.random}  # Sets the user-agent in the request headers; headers tell the server about the request.
    proxies = {'http': PROXY, 'https': PROXY} if PROXY else None  # Sets proxies if provided; otherwise, None (no proxy).
    for query in queries:  # Loops through the queries again.
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"  # Creates the search URL.
        for attempt in range(max_retries):  # Tries up to max_retries times.
            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=15)  # Sends an HTTP GET request; 'timeout=15' limits wait to 15 seconds.
                response.raise_for_status()  # Checks if the request failed (e.g., 404 or 500 error); raises an error if so.
                soup = BeautifulSoup(response.text, 'html.parser')  # Parses the response HTML with BeautifulSoup.
                if soup.find('div', id='captcha') or 'recaptcha' in response.text.lower() or 'enablejs' in response.text.lower():  # Checks for CAPTCHA in the response.
                    print(f"CAPTCHA detected in requests for query '{query}'. Saving HTML.")  # Prints if a CAPTCHA is found.
                    with open(f'captcha_page_requests_{query.replace(" ", "_")}.html', 'w', encoding='utf-8') as f:  # Saves the HTML for debugging.
                        f.write(response.text)  # Writes the response HTML to the file.
                    break  # Exits the attempt loop.
                
                results = soup.find_all('div', class_=re.compile('tF2Cxc|VwiC3b|yuRUbf|rllt__local|W4Efsd|rllt__details|section-result'))  # Finds result divs.
                for result in results[:5]:  # Loops through the top 5 results.
                    text = result.get_text(separator=' ', strip=True)  # Extracts text from each result.
                    raw_data.append(text)  # Adds text to the raw_data list.
                
                print(f"Retrieved {len(raw_data)} raw results from Google (requests) for query: {query}")  # Prints the number of results.
                if raw_data:  # If data was found, return it.
                    return raw_data
            except Exception as e:  # Catches request errors.
                print(f"Requests attempt {attempt + 1} failed for query '{query}': {e}")  # Prints the error.
                if attempt < max_retries - 1:  # If more attempts remain.
                    time.sleep(2 ** attempt)  # Waits longer each retry.
                continue  # Tries the next attempt.
    
    print("All Google scraping attempts failed.")  # Prints if both Selenium and requests fail.
    print(f"Final HTML sample: {driver.page_source[:500]}")  # Prints the first 500 characters of the final page for debugging.
    with open('final_google_page.html', 'w', encoding='utf-8') as f:  # Saves the final page HTML.
        f.write(driver.page_source)  # Writes the HTML to the file.
    return []  # Returns an empty list if all attempts fail.

# Function to process manually entered Google search results using Gemini AI.
def process_manual_google_input(category, location, max_attempts=2):
    """This function lets the user paste Google search results, and Gemini AI extracts business details like name, address, website, and phone."""
    attempts = 0  # Initializes a counter for user input attempts.
    while attempts < max_attempts:  # 'while' loop runs until attempts reach max_attempts.
        print("Manual Google input mode: Paste search results text (or press Enter to skip):")  # Prompts the user to paste text.
        print("Example: Digital Solutions Abbottabad 123 Jinnah Road, Abbottabad, Pakistan https://digitalsolutions.pk +92 300 123 4567")  # Shows an example input format.
        manual_text = input().strip()  # Gets user input and removes extra spaces; 'input' waits for user text, 'strip' removes leading/trailing spaces.
        if not manual_text and attempts < max_attempts - 1:  # 'if' checks if input is empty and more attempts remain.
            print("No input provided. Please try again or press Enter to skip.")  # Asks the user to try again.
            attempts += 1  # Increments the attempt counter; '+=' adds 1 to the variable.
            continue  # Skips to the next loop iteration.
        if not manual_text:  # If input is still empty after max attempts.
            print("No manual Google input provided. Skipping.")  # Informs the user we’re skipping.
            return []  # Returns an empty list.
        
        businesses = []  # Creates an empty list for business details.
        for line in manual_text.split('\n'):  # Splits input into lines; 'split' breaks text at newlines ('\n').
            prompt = f"""
            Extract business details from: "{line}"
            Provide JSON with:
            - name: Business name
            - address: Business address
            - website: Website URL (if available, else "N/A")
            - phone: Phone number (if available, else "N/A")
            If no relevant data, return an empty object.
            """  # Creates a prompt for Gemini AI to extract structured data from the input line; multi-line string uses triple quotes.
            try:  # Tries to process the line with Gemini AI.
                model = genai.GenerativeModel("gemini-1.5-flash")  # Creates a Gemini AI model; "gemini-1.5-flash" is the model name.
                response = model.generate_content(prompt)  # Sends the prompt to Gemini to process; 'generate_content' gets the AI’s response.
                response_text = response.text.strip()  # Gets the response text and removes extra spaces.
                if response_text.startswith('```json'):  # Checks if the response starts with a JSON code block.
                    response_text = response_text.strip('```json').strip('```').strip()  # Removes code block markers and extra spaces.
                data = json.loads(response_text)  # Converts the JSON text to a Python dictionary; 'json.loads' parses JSON.
                if data and 'name' in data and data['name'] and data['name'] != 'N/A':  # Checks if the data has a valid name; 'and' combines conditions.
                    data['location'] = location  # Adds the search location to the data.
                    data['source'] = 'Manual Google + Gemini'  # Notes the data source.
                    businesses.append(data)  # Adds the data to the businesses list.
            except Exception as e:  # Catches any errors during processing.
                print(f"Gemini Google input error for line '{line}': {e}")  # Prints the error for debugging.
                continue  # Skips to the next line.
        
        print(f"Extracted {len(businesses)} businesses from manual Google input with Gemini")  # Prints how many businesses were extracted.
        return businesses  # Returns the list of businesses.

# Function to process manually entered LinkedIn employee data using Gemini AI.
def process_manual_linkedin_input(category, location, max_attempts=2):
    """This function lets the user paste LinkedIn employee data, and Gemini AI extracts details like name, job title, and email."""
    attempts = 0  # Initializes the attempt counter.
    while attempts < max_attempts:  # Loops until max attempts are reached.
        print("Manual LinkedIn input mode: Paste employee data (name, job title, email) or press Enter to skip:")  # Prompts the user for input.
        print("Example: John Doe Digital Marketing Manager john.doe@example.com")  # Shows an example input format.
        manual_text = input().strip()  # Gets user input and removes extra spaces.
        if not manual_text and attempts < max_attempts - 1:  # Checks if input is empty and more attempts remain.
            print("No input provided. Please try again or press Enter to skip.")  # Asks the user to try again.
            attempts += 1  # Increments the attempt counter.
            continue  # Skips to the next iteration.
        if not manual_text:  # If input is still empty after max attempts.
            print("No manual LinkedIn input provided. Skipping.")  # Informs the user we’re skipping.
            return []  # Returns an empty list.
        
        employees = []  # Creates an empty list for employee details.
        for line in manual_text.split('\n'):  # Splits input into lines.
            prompt = f"""
            Extract employee details from: "{line}"
            Provide JSON with:
            - name: Employee name
            - job_title: Job title
            - email: Email (if available, else "N/A")
            If no relevant data, return an empty object.
            """  # Creates a prompt for Gemini AI to extract employee details.
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")  # Creates a Gemini AI model.
                response = model.generate_content(prompt)  # Sends the prompt to Gemini.
                response_text = response.text.strip()  # Gets and cleans the response text.
                if response_text.startswith('```json'):  # Checks for JSON code block.
                    response_text = response_text.strip('```json').strip('```').strip()  # Removes code block markers.
                data = json.loads(response_text)  # Converts JSON to a Python dictionary.
                if data and 'name' in data and data['name'] and data['name'] != 'N/A':  # Checks if the data has a valid name.
                    data['location'] = location  # Adds the location.
                    data['source'] = 'Manual LinkedIn + Gemini'  # Notes the source.
                    employees.append(data)  # Adds the data to the employees list.
            except Exception as e:  # Catches errors.
                print(f"Gemini LinkedIn input error for line '{line}': {e}")  # Prints the error.
                continue  # Skips to the next line.
        
        print(f"Extracted {len(employees)} employees from manual LinkedIn input with Gemini")  # Prints the number of employees extracted.
        return employees  # Returns the list of employees.

# Function to process raw scraped data with Gemini AI to extract structured business data.
def process_with_gemini(raw_data, category, location):
    """This function uses Gemini AI to turn raw text from Google searches into structured business data, or generates fake data if none is available."""
    businesses = []  # Creates an empty list for business details.
    
    if not raw_data:  # 'if not' checks if raw_data is empty.
        print("No scraped data. Generating mock data with Gemini...")  # Informs the user we’re creating fake data.
        prompt = f"""
        Generate a list of 3 fictional digital marketing agencies in {location}. For each, provide:
        - name: Business name (unique)
        - address: Business address
        - website: Website URL
        - phone: Phone number
        Format as a JSON list of objects.
        """  # Creates a prompt for Gemini to generate 3 fake businesses.
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # Creates a Gemini AI model.
            response = model.generate_content(prompt)  # Sends the prompt to Gemini.
            response_text = response.text.strip()  # Gets and cleans the response.
            print(f"Raw Gemini mock data: {response_text}")  # Prints the raw response for debugging.
            if response_text.startswith('```json'):  # Checks for JSON code block.
                response_text = response_text.strip('```json').strip('```').strip()  # Removes code block markers.
            mock_data = json.loads(response_text)  # Converts JSON to a Python list of dictionaries.
            for item in mock_data:  # Loops through each fake business.
                item['location'] = location  # Adds the location.
                item['source'] = 'Gemini Mock Data'  # Notes the source as mock data.
                businesses.append(item)  # Adds the business to the list.
            print(f"Generated {len(businesses)} mock businesses with Gemini")  # Prints the number of mock businesses.
            return businesses  # Returns the mock data.
        except Exception as e:  # Catches errors.
            print(f"Gemini mock data generation failed: {e}")  # Prints the error.
            return [  # Returns hardcoded fake data as a last resort.
                {
                    "name": "Mock Agency 1",
                    "address": "123 Mock Street, Abbottabad, Pakistan",
                    "website": "https://mockagency1.pk",
                    "phone": "+92 300 111 2222",
                    "location": location,
                    "source": "Fallback Mock Data"
                },
                {
                    "name": "Mock Agency 2",
                    "address": "456 Mock Road, Abbottabad, Pakistan",
                    "website": "https://mockagency2.pk",
                    "phone": "+92 300 222 3333",
                    "location": location,
                    "source": "Fallback Mock Data"
                },
                {
                    "name": "Mock Agency 3",
                    "address": "789 Mock Avenue, Abbottabad, Pakistan",
                    "website": "https://mockagency3.pk",
                    "phone": "+92 300 333 4444",
                    "location": location,
                    "source": "Fallback Mock Data"
                }
            ]  # This list of dictionaries is returned if Gemini fails.
    
    for text in raw_data:  # Loops through each piece of raw text.
        print(f"Processing raw text: {text[:100]}...")  # Prints the first 100 characters of the text for debugging.
        prompt = f"""
        Extract business details from: "{text}"
        Provide JSON with:
        - name: Business name
        - address: Business address
        - website: Website URL (if available, else "N/A")
        - phone: Phone number (if available, else "N/A")
        If no relevant data, return an empty object.
        """  # Creates a prompt for Gemini to extract details from the text.
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # Creates a Gemini AI model.
            response = model.generate_content(prompt)  # Sends the prompt to Gemini.
            response_text = response.text.strip()  # Gets and cleans the response.
            if response_text.startswith('```json'):  # Checks for JSON code block.
                response_text = response_text.strip('```json').strip('```').strip()  # Removes code block markers.
            data = json.loads(response_text)  # Converts JSON to a Python dictionary.
            if data and 'name' in data and data['name'] and data['name'] != 'N/A':  # Checks if the data has a valid name.
                data['location'] = location  # Adds the location.
                data['source'] = 'Google + Gemini'  # Notes the source.
                businesses.append(data)  # Adds the data to the businesses list.
        except Exception as e:  # Catches errors.
            print(f"Gemini processing error for text: {e}")  # Prints the error.
            continue  # Skips to the next text.
        
        print(f"Extracted {len(businesses)} businesses with Gemini")  # Prints the number of businesses extracted.
        return businesses  # Returns the businesses list.

# Placeholder function for LinkedIn scraping (not implemented due to restrictions).
def scrape_linkedin(category, location, driver):
    """This function is a placeholder to remind users to use LinkedIn’s API for legal data access instead of scraping."""
    print("LinkedIn scraping is restricted. Consider using LinkedIn API for team member data.")  # Informs the user that scraping LinkedIn is not allowed.
    print("Visit https://www.linkedin.com/developers/ for API access.")  # Provides the URL for LinkedIn’s API.
    return []  # Returns an empty list since scraping isn’t implemented.

# Function to clean and validate collected data.
def clean_data(data):
    """This function removes invalid or duplicate entries but keeps mock data to ensure we have valid results."""
    cleaned_data = []  # Creates an empty list for valid data.
    seen_names = set()  # Creates a set to track unique business names; a set stores unique items.
    
    for item in data:  # Loops through each data item.
        name = item.get('name', '')  # Gets the name or an empty string if missing.
        if name and name != 'N/A':  # Checks if the name is valid (not empty or 'N/A').
            if name not in seen_names:  # 'not in' checks if the name hasn’t been seen before.
                cleaned_data.append(item)  # Adds the item to the cleaned list.
                seen_names.add(name)  # Adds the name to the set; 'add' puts an item in the set.
    
    print(f"Cleaned data: {len(cleaned_data)} valid entries")  # Prints the number of valid entries.
    return cleaned_data  # Returns the cleaned data list.

# Function to save data to a CSV file.
def save_to_csv(data, filename):
    """This function saves the cleaned data to a CSV file, like a spreadsheet."""
    if not data:  # Checks if the data list is empty.
        print("No data to save.")  # Informs the user there’s nothing to save.
        return  # Exits the function.
    df = pd.DataFrame(data)  # Converts the data list to a pandas DataFrame (table); 'pd.DataFrame' creates the table.
    df.to_csv(filename, index=False, encoding='utf-8')  # Saves the DataFrame to a CSV file; 'index=False' skips row numbers, 'utf-8' ensures proper text encoding.
    print(f"CSV saved to {filename}")  # Prints the file name where data was saved.

# Function to save data to a JSON file.
def save_to_json(data, filename):
    """This function saves the cleaned data to a JSON file, a structured data format."""
    if not data:  # Checks if the data list is empty.
        return  # Exits the function.
    with open(filename.replace('.csv', '.json'), 'w', encoding='utf-8') as f:  # Opens a JSON file; 'replace' changes '.csv' to '.json' in the filename.
        json.dump(data, f, indent=2)  # Writes the data to the JSON file; 'indent=2' makes it readable with indentation.
    print(f"JSON saved to {filename.replace('.csv', '.json')}")  # Prints the JSON file name.

# Main function to coordinate all tasks.
def main():
    """This function runs the entire program: scraping Google, processing data, cleaning it, and saving it to files."""
    driver = None  # Initializes the Selenium driver as None (no browser yet).
    try:  # Tries to run the main tasks, catching errors to avoid crashes.
        print(f"Scraping Google for {BUSINESS_CATEGORY} in {LOCATION}...")  # Informs the user we’re starting Google scraping.
        # Try Google Places API first.
        google_data = scrape_google_places(BUSINESS_CATEGORY, LOCATION)  # Calls the function to scrape using Google Places API.
        
        # If the API returns no results, try Selenium.
        if not google_data:  # Checks if google_data is empty.
            print("Google Places API returned no results. Falling back to Selenium...")  # Informs the user we’re switching to Selenium.
            driver = setup_driver()  # Sets up the Selenium browser.
            raw_google_data = scrape_google_selenium(BUSINESS_CATEGORY, LOCATION, driver)  # Scrapes Google with Selenium.
            google_data = process_with_gemini(raw_google_data, BUSINESS_CATEGORY, LOCATION)  # Processes the raw data with Gemini AI.
        
        # If Selenium fails, try manual input.
        if not google_data:  # Checks if google_data is still empty.
            print("Google scraping failed. Trying manual Google input...")  # Informs the user we’re switching to manual input.
            google_data = process_manual_google_input(BUSINESS_CATEGORY, LOCATION)  # Processes manual Google input.
        
        print(f"Processing LinkedIn data for {BUSINESS_CATEGORY} in {LOCATION}...")  # Informs the user we’re starting LinkedIn processing.
        linkedin_data = scrape_linkedin(BUSINESS_CATEGORY, LOCATION, driver)  # Calls the LinkedIn placeholder function.
        if not linkedin_data:  # Checks if linkedin_data is empty.
            print("LinkedIn scraping skipped. Trying manual LinkedIn input...")  # Informs the user we’re switching to manual input.
            linkedin_data = process_manual_linkedin_input(BUSINESS_CATEGORY, LOCATION)  # Processes manual LinkedIn input.
        
        combined_data = google_data + linkedin_data  # Combines Google and LinkedIn data; '+' joins two lists.
        cleaned_data = clean_data(combined_data)  # Cleans the combined data to remove duplicates.
        save_to_csv(cleaned_data, OUTPUT_FILE)  # Saves the cleaned data to a CSV file.
        save_to_json(cleaned_data, OUTPUT_FILE)  # Saves the cleaned data to a JSON file.
    finally:  # 'finally' runs no matter what, even if errors occur.
        if driver:  # Checks if a Selenium driver was created.
            driver.quit()  # Closes the browser to free up resources; 'quit' shuts down the browser.

# Function to schedule periodic scraping.
def schedule_scraping():
    """This function schedules the main function to run daily at 8 AM."""
    print("Starting scheduled scraping at 08:00 daily...")  # Informs the user scheduling is starting.
    schedule.every().day.at("08:00").do(main)  # Sets the main function to run daily at 8 AM; 'schedule.every().day.at' sets the time.
    while True:  # 'while True' creates an infinite loop to keep checking for scheduled tasks.
        schedule.run_pending()  # Runs any scheduled tasks that are due; 'run_pending' checks the schedule.
        time.sleep(60)  # Waits 60 seconds before checking again; 'sleep' pauses execution.

# This checks if the script is run directly (not imported as a module).
if __name__ == "__main__":  # '__name__' is a special Python variable; '__main__' means the script is running directly.
    if SCHEDULE_ENABLED:  # Checks if scheduling is enabled (True).
        #print("its not working now")  # Commented-out debug message.
        schedule_scraping()  # Starts the scheduled scraping.
    else:  # If scheduling is disabled (False).
        main()  # Runs the main function once.