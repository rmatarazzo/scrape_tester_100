import os
import json
import time
import logging
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
import pandas as pd # Prettify the CSV report

#logger.info(f"Output directory '{output_dir}' created or already exists.")
# output_dir = 'data_output_files' # create a directory to store the output files
# os.makedirs(output_dir, exist_ok=True)

# List to keep track of WebDriver instances
drivers = []

def timestamped_filename(base_filename):  # base_filename (str): The base name of the file without the extension.
    """Generate a filename with a timestamp to uniquely identify the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"  # str: The timestamped filename including the original base name and extension.

# def configure_logging():
#     """Configure logging settings with a timestamped log file."""
#     log_filename = timestamped_filename("debug.log")
#     logging.basicConfig(
#         level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
#         handlers=[
#             logging.FileHandler(log_filename),  # Log to a timestamped file
#             logging.StreamHandler()  # Also log to console
#         ]
#     )
#     logger = logging.getLogger(__name__)
#     logger.info(f"Logging configured. Log file: {log_filename}")
#     return logger

# def configure_logging():
#     """Configure logging settings with a timestamped log file."""
#     if len(logging.getLogger().handlers) > 0:
#         # Logging is already configured
#         return logging.getLogger(__name__)

#     log_filename = timestamped_filename("debug.log")
#     logging.basicConfig(
#         level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
#         handlers=[
#             logging.FileHandler(log_filename),  # Log to a timestamped file
#             logging.StreamHandler()  # Also log to console
#         ]
#     )
#     logger = logging.getLogger(__name__)
#     logger.info(f"Logging configured. Log file: {log_filename}")
#     return logger

def configure_logging():
    """Configure logging settings with a timestamped log file."""
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        # Logging is already configured
        return logger

    log_filename = timestamped_filename("debug.log")
    file_handler = logging.FileHandler(log_filename)
    stream_handler = logging.StreamHandler()

    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[file_handler, stream_handler]
    )

    logger.info(f"Logging configured. Log file: {log_filename}")
    return logger

# Configure logging
logger = configure_logging()

output_dir = 'data_output_files' # create a directory to store the output files
os.makedirs(output_dir, exist_ok=True)
#logger.info(f"Output directory '{output_dir}' created or already exists.")

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

class GoogleSearchLoader:
    """A class to load and process Google search results."""
    def __init__(self, query):
        """Initialize the GoogleSearchLoader object with a search query."""
        self.query = query
        self.driver = webdriver.Chrome()
        drivers.append(self.driver)  # Add the WebDriver instance to the list
        #logger.info(f"WebDriver instance created and added to the list for query: {self.query}")

    # def load_results(self):
    #     """Load search results for the query."""
    #     # Simulate loading results
    #     total_steps = 10
    #     for step in range(total_steps):
    #         time.sleep(0.5)  # Simulate some work
    #         progress_bar.progress((step + 1) / total_steps * 0.4)  # 40% of the progress for loading results
    #         logger.debug(f"Loading step {step + 1}/{total_steps} for query: {self.query}")

    def load_and_scroll(self):
        """Load search results and scroll until at least 100 items or no new items are found
        and return the HTML content of the loaded pages."""
        options = Options()
        # options.add_argument('--headless')
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
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.fl'))
                        )
                        more_results_button.click()
                        time.sleep(2)
                    except Exception:
                        break
            return collected_html
        finally:
            driver.quit() #processes are terminated.

    def save_html(self, html_content, base_filename="Google_search_results.html"): # html_content (str): The HTML content to save and base_filename (str): The base name of the file without the extension.
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

    def save_results_to_json(self, results, base_filename="parsed_Google_search_results.json"):  
        """Save the parsed results to a timestamped JSON file.
        results (list): The list of parsed results and base_filename 
        (str): The base name of the file without the extension.
         """
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

        return metadata, None  # Tuple containing the metadata dictionary and any error message.
    except Exception as e:
        return None, str(e)
    finally:
        if driver:
            driver.quit()
      
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
    return results

def generate_report(test_results, query_topic):
    """Generate a text-based report summarizing the test results.
      Args:     test_results (list): dictionaries list containing test results 
                query_topic (str): The search query topic used for testing.
      Returns   str: A formatted string representing the report.
      """
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

    return "\n".join(report_lines)

def save_report_to_csv(test_results, query_topic):
    """Save the test results to a CSV file with a timestamped filename.
    Args:      test_results (list): A list of dictionaries containing the test results
               query_topic (str): The search query topic used for testing.
    Returns:   str: The path to the saved CSV file.
    """ 
    timestamped_csv = timestamped_filename("Google_links_scrape_report.csv")
    with open(timestamped_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'status', 'title', 'description', 'keywords', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in test_results:
            writer.writerow(result)
    
    return timestamped_csv # str: The path to the saved CSV file.

def exit_program():
    """Terminate all WebDriver instances and exit the program gracefully."""
    for driver in drivers:
        driver.quit()
    st.stop()

def main():
    """Main function to orchestrate the scraping and testing workflow using Streamlit."""
    st.title('Scrape Tester 100')
    st.write('The program uses the Chrome webbrowser to perform a Google search query based on user input.  It collects the HTML information from the Google search pages for a minimum of 100 items.  Those items are parsed into a dictionary of 100 links along with there title and snippet.  The links are individually tested to see if they can be web scraped.  The results are outputted to a test results report.')
    query = st.text_input('Please enter the Google search query:')
   
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
            output_filename = timestamped_filename('parsed_Google_links_scrape_test.json')
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, ensure_ascii=False, indent=4)
            st.write(f"Test results saved to {output_filename}")

            # Generate the report
            report = generate_report(test_results, query)
            report_filename = timestamped_filename('Google_links_scrape_report.txt')
            
            # Prettify the text report
            def prettify_text_report(report):
                # Example: Add headers, line breaks, and indentation
                pretty_report = "=== Report ===\n\n"
                pretty_report += report.replace('\n', '\n    ')
                return pretty_report

            pretty_report = prettify_text_report(report)
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(pretty_report)
            st.write(f"Report saved to {report_filename}")

            # Save the report to a CSV file
            csv_filename = save_report_to_csv(test_results, query)
            #csv_filename = os.path.join(output_dir, 'your_csv_filename.csv')  # Replace 'your_csv_filename.csv' with the actual filename


            def prettify_csv_report(csv_filename):
                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_filename)
                
                # Example: Sort the DataFrame and format columns
                df = df.sort_values(by=['link'])  # Replace 'column_name' with the actual column to sort by
                
                # Save the prettified DataFrame back to CSV
                csv_filename = os.path.join(output_dir, 'Google_links_scrape_report.csv')  # Replace 'your_csv_filename.csv' with the actual filename
                df.to_csv(csv_filename, index=False)

            prettify_csv_report(csv_filename)
            st.write(f"CSV report saved to {csv_filename}")

    if st.button('Exit Program'):
        exit_program()

if __name__ == "__main__":
    try:
        main()
    finally:
        # Ensure all WebDriver instances are closed
        for driver in drivers:
            driver.quit()

