import os
import json
import time
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
import streamlit as st
import csv

def timestamped_filename(base_filename):  # base_filename (str): The base name of the file without the extension.
    """Generate a filename with a timestamp to uniquely identify the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"  # str: The timestamped filename including the original base name and extension.

class GoogleSearchLoader:  # Attributes: query (str): The search query string.
    """A class to load and process Google search results."""
    def __init__(self, query):  # query (str): The search query string.
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
                # Wait for the search results to load
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.g')))

                search_items = driver.find_elements(By.CSS_SELECTOR, 'div.g')
                num_results += len(search_items)
                collected_html += driver.page_source

                if num_results >= 100:
                    break

                # Try to find the "Next" button and click it
                try:
                    next_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a#pnnext'))
                    )
                    next_button.click()
                    time.sleep(2)  # Allow time for the page to load
                except Exception:
                    try:
                        more_results_button = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="U8S5sf"]'))
                        )
                        more_results_button.click()
                        time.sleep(2)  # Allow time for the page to load
                    except Exception:
                        break  # No more results available

            return collected_html
        finally:
            driver.quit()  # Ensure the WebDriver session is closed and all Chrome processes are terminated.

    def save_html(self, html_content, base_filename="Google_search_results.html"): # html_content (str): The HTML content to save and base_filename (str): The base name of the file without the extension.
        """Save the HTML content to a timestamped file."""
        timestamped_file = timestamped_filename(base_filename)
        with open(timestamped_file, 'w', encoding='utf-8') as file:
            file.write(html_content)
        return timestamped_file # str: The timestamped filename of the saved HTML file.

    def save_results_to_json(self, results, base_filename="parsed_Google_search_results.json"): # results (list): The list of parsed results and base_filename (str): The base name of the file without the extension.
        """Save the parsed results to a timestamped JSON file."""
        json_filename = timestamped_filename(base_filename)
        with open(json_filename, "w", encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        return json_filename # str: The path to the saved JSON file.

    def parse_items(self, html_content):
        """Parse search items from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser') # html_content (str): The HTML content to parse.
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
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        return results # list: A list of dictionaries containing parsed search items.

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
            
        driver.quit()
        return metadata, None  # Tuple containing the metadata dictionary and any error message.
    except Exception as e:
        return None, str(e)

def test_link(link_info): # link_info (dict): A dictionary containing the link and optional error handling.
    """Test a single link by retrieving its metadata and returning a status."""
    link = link_info['link']
    metadata, error = get_page_metadata(link)
    if error:
        return {'link': link, 'status': 'error', 'error': error}
    else:
        return {'link': link, 'status': 'success', **metadata} # dict: A dictionary with the link status and optionally error details.

def test_links_concurrently(search_results): # search_results (list): A list of dictionaries representing links to test.
    """Test a list of links concurrently and collect the results."""
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_link, item): item for item in search_results}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    return results # list: A list of dictionaries containing the test results for each link.

def generate_report(test_results, query_topic): # test_results (list): A list of dictionaries containing the test results and query_topic (str): The search query topic used for testing.
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

    return "\n".join(report_lines) # str: A formatted string representing the report.

def save_report_to_csv(test_results, query_topic): # test_results (list): A list of dictionaries containing the test results and query_topic (str): The search query topic used for testing.
    """Save the test results to a CSV file with a timestamped filename."""
    timestamped_csv = timestamped_filename("links_scrape_report.csv")
    with open(timestamped_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'status', 'title', 'description', 'keywords', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in test_results:
            writer.writerow(result)
    
    return timestamped_csv # str: The path to the saved CSV file.

def main():
    """Main function to orchestrate the scraping and testing workflow using Streamlit."""
    st.title('Google Search Scrape Test')
    query = st.text_input('Please enter the search query topic:')
    
    if query:
        if st.button('Run Scrape Test'):
            loader = GoogleSearchLoader(query=query)

            # Load and scroll through the search results, then save the HTML content
            html_content = loader.load_and_scroll()
            html_filename = loader.save_html(html_content)
            st.write(f"HTML content saved to {html_filename}")

            # Parse the HTML content to extract search results
            search_results = loader.parse_items(html_content)
            st.write(f"Extracted {len(search_results)} items.")

            # Ensure we have at least 100 unique links
            if len(search_results) < 100:
                st.write(f"Collected only {len(search_results)} links, retrying to get more...")
                while len(search_results) < 100:
                    html_content = loader.load_and_scroll()
                    search_results.extend(loader.parse_items(html_content))
                    search_results = list({item['link']: item for item in search_results if item['link']}.values())
                    st.write(f"Collected {len(search_results)} links so far...")

            # Save the parsed search results to a JSON file
            json_filename = loader.save_results_to_json(search_results[:100])  # Ensure we have at most 100 links
            st.write(f"Parsed search results saved to {json_filename}")

            # Load the parsed search results from the JSON file
            with open(json_filename, 'r', encoding='utf-8') as f:
                search_results = json.load(f)

            # Test the links concurrently and save the results
            test_results = test_links_concurrently(search_results)
            output_filename = timestamped_filename('links_scrape_test.json')
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, ensure_ascii=False, indent=4)
            st.write(f"Test results saved to {output_filename}")

            # Generate the report
            report = generate_report(test_results, query)
            report_filename = timestamped_filename('links_scrape_report.txt')
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            st.write(f"Report saved to {report_filename}")

            # Save the report to a CSV file
            csv_filename = save_report_to_csv(test_results, query)
            st.write(f"CSV report saved to {csv_filename}")

if __name__ == "__main__":
    main()
