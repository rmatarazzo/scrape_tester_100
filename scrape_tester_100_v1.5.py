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
import tkinter as tk
from tkinter import simpledialog
import csv

def timestamped_filename(base_filename):
    """
    Generate a filename with a timestamp.

    Args:
        base_filename (str): The base filename without timestamp.

    Returns:
        str: The filename with appended timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"

class GoogleSearchLoader:
    """
    Class to load Google search results and scroll through pages to collect data.

    Attributes:
        query (str): The search query to be used for Google search.
    """

    def __init__(self, query):
        """
        Initialize the GoogleSearchLoader with a search query.

        Args:
            query (str): The search query to be used for Google search.
        """
        self.query = query

    def load_and_scroll(self):
        """
        Load search results and scroll until at least 100 items or no new items are found.

        Returns:
            str: Collected HTML content from the search results pages.
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
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
                next_button = driver.find_element(By.CSS_SELECTOR, 'a#pnnext')
                next_button.click()
            except:
                break

        driver.quit()
        return collected_html

    def parse_items(self, html_content):
        """
        Parse search result items from the HTML content.

        Args:
            html_content (str): HTML content of the search results.

        Returns:
            list: A list of parsed search result items with titles and links.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        for item in soup.select('div.g'):
            title_element = item.select_one('h3')
            link_element = item.select_one('a')
            if title_element and link_element:
                results.append({
                    'title': title_element.get_text(),
                    'link': link_element['href']
                })
        return results

    def save_results_to_json(self, results):
        """
        Save search results to a JSON file.

        Args:
            results (list): List of search result items to be saved.

        Returns:
            str: The filename of the saved JSON file.
        """
        filename = timestamped_filename('search_results.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        return filename

def test_link(link):
    """
    Test a single link to check its availability and response time.

    Args:
        link (str): The URL to be tested.

    Returns:
        dict: The test result containing the URL, status, and response time.
    """
    result = {'link': link, 'status': 'failed', 'response_time': None}
    try:
        start_time = time.time()
        response = requests.head(link, allow_redirects=True, timeout=5)
        result['response_time'] = time.time() - start_time
        if response.status_code == 200:
            result['status'] = 'success'
    except Exception as e:
        result['error'] = str(e)
    return result

def test_links_concurrently(links):
    """
    Test multiple links concurrently.

    Args:
        links (list): List of URLs to be tested.

    Returns:
        list: A list of test results for each URL.
    """
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_link = {executor.submit(test_link, link['link']): link for link in links}
        for future in as_completed(future_to_link):
            link = future_to_link[future]
            try:
                result = future.result()
                result.update({'title': link['title']})
                results.append(result)
            except Exception as e:
                results.append({'link': link['link'], 'title': link['title'], 'status': 'failed', 'error': str(e)})
    return results

def generate_report(test_results, query):
    """
    Generate a report from test results.

    Args:
        test_results (list): List of test results.
        query (str): The search query used.

    Returns:
        str: Generated report as a string.
    """
    report_lines = [f"Search Query: {query}", f"Total Results: {len(test_results)}"]
    for result in test_results:
        report_lines.append(f"Title: {result['title']}, Link: {result['link']}, Status: {result['status']}, Response Time: {result.get('response_time', 'N/A')}")
    return "\n".join(report_lines)

def save_report_to_csv(test_results, query):
    """
    Save the report to a CSV file.

    Args:
        test_results (list): List of test results.
        query (str): The search query used.

    Returns:
        str: The filename of the saved CSV file.
    """
    filename = timestamped_filename('search_report.csv')
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Query', 'Title', 'Link', 'Status', 'Response Time'])
        for result in test_results:
            writer.writerow([query, result['title'], result['link'], result['status'], result.get('response_time', 'N/A')])
    return filename

def main():
    """
    Main function to run the entire process of searching, parsing, testing, and reporting.
    """
    root = tk.Tk()
    root.withdraw()
    query = simpledialog.askstring("Input", "Please enter your search query:")

    if query:
        loader = GoogleSearchLoader(query)

        # Load and parse search results
        html_content = loader.load_and_scroll()
        search_results = loader.parse_items(html_content)
        print(f"Extracted {len(search_results)} items.")

        # Ensure we have at least 100 unique links
        if len(search_results) < 100:
            print(f"Collected only {len(search_results)} links, retrying to get more...")
            while len(search_results) < 100:
                html_content = loader.load_and_scroll()
                search_results.extend(loader.parse_items(html_content))
                search_results = list({item['link']:item for item in search_results if item['link']}.values())
                print(f"Collected {len(search_results)} links so far...")

        # Save the parsed search results to a JSON file
        json_filename = loader.save_results_to_json(search_results[:100])  # Ensure we have at most 100 links
        print(f"Parsed search results saved to {json_filename}")

        # Load the parsed search results from the JSON file
        with open(json_filename, 'r', encoding='utf-8') as f:
            search_results = json.load(f)

        # Test the links concurrently and save the results
        test_results = test_links_concurrently(search_results)
        output_filename = timestamped_filename('links_scrape_test.json')
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)
        print(f"Test results saved to {output_filename}")

        # Generate the report
        report = generate_report(test_results, query)
        report_filename = timestamped_filename('links_scrape_report.txt')
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {report_filename}")

        # Save the report to a CSV file
        csv_filename = save_report_to_csv(test_results, query)
        print(f"CSV report saved to {csv_filename}")

    else:
        print("No query provided. Exiting.")

if __name__ == "__main__":
    main()
