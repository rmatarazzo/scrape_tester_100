from datetime import datetime
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json
import csv
import pandas as pd
import streamlit as st

output_dir = 'data_output_files'  # create a directory to store the output files
os.makedirs(output_dir, exist_ok=True)

# List to keep track of WebDriver instances
drivers = []

def timestamped_filename(base_filename):  # base_filename (str): The base name of the file without the extension.
    """Generate a filename with a timestamp to uniquely identify the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"  # str: The timestamped filename including the original base name and extension.

class GoogleSearchLoader:
    """A class to load and process Google search results."""
    def __init__(self, query):
        """Initialize the GoogleSearchLoader object with a search query."""
        self.query = query

    def load_and_scroll(self):
        """Load search results and scroll until at least 100 items or no new items are found
        and return the HTML content of the loaded pages."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(f"https://www.google.com/search?q={quote_plus(self.query)}")
            num_results = 0
            collected_html = ""
            wait = WebDriverWait(driver, 10)

            while num_results < 100:
                # Add your scrolling and result collection logic here
                pass
                
            return collected_html
        finally:
            driver.quit()  # Ensure the driver is closed

    def save_html(self, html_content, base_filename="Google_search_results.html"):  # html_content (str): The HTML content to save and base_filename (str): The base name of the file without the extension.
        """Save the HTML content to a timestamped file with pretty print."""
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        pretty_html = soup.prettify()

        # Generate the timestamped filename
        timestamped_file = timestamped_filename(base_filename)
    
        # Write the pretty-printed HTML to the file
        with open(timestamped_file, 'w', encoding='utf-8') as file:
            file.write(pretty_html)
    
        return timestamped_file  # str: The timestamped filename of the saved HTML file.    

    def save_results_to_json(self, results, base_filename="parsed_Google_search_results.json"):  # results (list): The list of parsed results and base_filename (str): The base name of the file without the extension.
        """Save the parsed results to a timestamped JSON file."""
        json_filename = timestamped_filename(base_filename)
        with open(json_filename, "w", encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        return json_filename  # str: The path to the saved JSON file.

    def parse_items(self, html_content):
        """Parse search items from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')  # html_content (str): The HTML content to parse.
        results = []
        search_items = soup.select('div.g')  # Adjust the selector as needed
        for item in search_items:
            title_div = item.select_one('h3')
            title = title_div.text if title_div else "No title"
            link_tag = item.select_one('a')
            link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None
            snippet_div = item.select_one('div.kb0PBd')
            snippet = snippet_div.text if snippet_div else "No snippet available"
            if link:
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet
                })
        return results  # list: A list of dictionaries containing parsed search items.

def get_page_metadata(link):
    """
    Retrieve metadata (title, description, keywords) from a webpage using Selenium.
    
    Parameters:
    - link (str): The URL of the webpage.
    
    Returns:
    tuple: A tuple containing the metadata dictionary and any error message.
    """
    try:
        # Setup Selenium WebDriver
        options = Options()
        options.add_argument('--headless')  # Run headlessly
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(link)
        
        # Wait for the page to fully load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Extract title
        title = driver.title
        
        # Initialize metadata dictionary
        metadata = {
            "title": title,
            "description": "",
            "keywords": ""
        }
        
        # Extract meta tags for description and keywords with improved error handling
        try:
            description_element = driver.find_element(By.XPATH, "//meta[@name='description']")
            metadata['description'] = description_element.get_attribute('content') if description_element else "No description found"
        except Exception:
            # Instead of returning immediately, set an error message in the metadata dictionary
            metadata['description'] = "Description meta tag not found."
        
        try:
            keywords_element = driver.find_element(By.XPATH, "//meta[@name='keywords']")
            metadata['keywords'] = keywords_element.get_attribute('content') if keywords_element else "No keywords found"
        except Exception:
            # Instead of returning immediately, set an error message in the metadata dictionary
            metadata['keywords'] = "Keywords meta tag not found."

        return metadata, None  # Tuple containing the metadata dictionary and any error message.
    except Exception as e:
        return None, str(e)
    finally:
        if driver:
            driver.quit()
      
def test_link(link_info):  # link_info (dict): A dictionary containing the link and optional error handling.
    """Test a single link by retrieving its metadata and returning a status."""
    link = link_info['link']
    metadata, error = get_page_metadata(link)
    if error:
        return {'link': link, 'status': 'error', 'error': error}
    else:
        return {'link': link, 'status': 'success', **metadata}  # dict: A dictionary with the link status and optionally error details.

def test_links_concurrently(search_results):  # search_results (list): A list of dictionaries representing links to test.
    """Test a list of links concurrently and collect the results."""
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_link, item): item for item in search_results}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    return results  # list: A list of dictionaries containing the test results for each link.

def generate_report(test_results, query_topic):  # test_results (list): A list of dictionaries containing the test results and query_topic (str): The search query topic used for testing.
    """Generate a text-based report summarizing the test results."""
    success_count = sum(1 for result in test_results if result['status'] == 'success')
    error_count = len(test_results) - success_count

    report_lines = [
        f"Link Scrape Test Report for query: {query_topic}",
        f"Total Links Tested: {len(test_results)}",
        f"Total Successes: {success_count}",
        f"Total Errors: {error_count}",
        "",
        "Details:"
    ]

    for result in test_results:
        if result['status'] == 'success':
            report_lines.append(
                f"SUCCESS: {result['link']} - Title: {result['title']} - Description: {result['description']} - Keywords: {result['keywords']}"
            )
        else:
            report_lines.append(f"ERROR: {result['link']} - Error: {result['error']}")

    return "\n".join(report_lines)  # str: A formatted string representing the report.

def save_report_to_csv(test_results, query_topic):  # test_results (list): A list of dictionaries containing the test results and query_topic (str): The search query topic used for testing.
    """Save the test results to a CSV file with a timestamped filename."""
    timestamped_csv = timestamped_filename("Google_links_scrape_report.csv")
    with open(timestamped_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'status', 'title', 'description', 'keywords', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in test_results:
            writer.writerow(result)
    
    return timestamped_csv  # str: The path to the saved CSV file.

def prettify_csv_report(csv_filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_filename)
    
    # Example: Sort the DataFrame and format columns
    df = df.sort_values(by=['link'])  # Replace 'column_name' with the actual column to sort by
    
    # Save the prettified DataFrame back to CSV
    csv_filename = os.path.join(output_dir, 'Google_links_scrape_report.csv')  # Replace 'your_csv_filename.csv' with the actual filename
    df.to_csv(csv_filename, index=False)

    return csv_filename  # Return the path to the prettified CSV file


def main():
    # Example search query
    query = "example search query"
    
    # Initialize GoogleSearchLoader with the query
    search_loader = GoogleSearchLoader(query)
    
    # Perform the search and process results
    search_loader.perform_search()
    search_results = search_loader.process_results()
    
    # Test the links concurrently
    test_results = test_links_concurrently(search_results)
    
    # Save the test results to a CSV file
    csv_filename = timestamped_filename("search_results.csv")
    csv_filepath = os.path.join(output_dir, csv_filename)
    with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'status', 'metadata']  # Adjust fieldnames as needed
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in test_results:
            writer.writerow(result)
    
    # Prettify the CSV report
    prettify_csv_report(csv_filepath)
    st.write(f"CSV report saved to {csv_filepath}")

if __name__ == "__main__":
    main()