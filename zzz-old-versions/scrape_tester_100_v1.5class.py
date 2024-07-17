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
    """Generate a filename with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"

class GoogleSearchLoader:
    def __init__(self, query):
        self.query = query

    def load_and_scroll(self):
        """Load search resultset and scroll until at least 100 items or no new items are found."""
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
            # Wait for the search results to load on the Google Search results page
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
                        EC.element_to_be_clickable((By.XPATH, '//a[contains(., "More results")]'))
                    )
                    more_results_button.click()
                    time.sleep(2)  # Allow time for more results to load
                except Exception:
                    print("No more pages or unable to load more results.")
                    break  # No new items or next/more results button was not found.
        
        driver.quit()
        return collected_html

    def save_html(self, html_content, base_filename="google_search_results.html"):
        """Save the HTML content to a timestamped file."""
        timestamped_file = timestamped_filename(base_filename)
        with open(timestamped_file, 'w', encoding='utf-8') as file:
            file.write(html_content)
        return timestamped_file

tags_list = ["//div[contains(@style, '-webkit-line-clamp:2')]", ""]

    def parse_items(self, html_content):
        """Parse search items from HTML content using BeautifulSoup and return the results_list to calling namespace."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results_list = []
        search_items = soup.select('div.g')  # Adjust the selector as needed
        for item in search_items:
            title_div = item.select_one('h3')
            title = title_div.text if title_div else "No title"
            link_tag = item.select_one('a')
            link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None
            snippet_div = item.select_one('div.kb0PBd')
            snippet = snippet_div.text if snippet_div else "No snippet available"
            if link:
                results_list.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        return results_list

    def save_results_to_json(self, results_list, base_filename="parsed_search_results.json"):
        """Save the parsed results_list to a timestamped JSON file."""
        json_filename = timestamped_filename(base_filename)
        with open(json_filename, "w", encoding='utf-8') as json_file:
            json.dump(results_list, json_file, ensure_ascii=False, indent=4)
        return json_filename

def get_page_metadata(link):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(link)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = driver.title
        description = soup.find('meta', attrs={'name': 'description'})
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        
        page_metadata = {
            "title": title,
            "description": description['content'] if description else "No description",
            "keywords": keywords['content'] if keywords else "No keywords"
        }
        
        driver.quit()
        return page_metadata, None
    except Exception as e:
        return None, str(e)

# For debugging purposes to see if get_page_metadata() works
#link = "https://www.allaboutbirds.org/news/binoculars-and-beyond-nine-tips-for-beginning-bird-watchers/"
#get_page_metadata(link)

def test_link(link_info):
    link = link_info['link']
    print(f"Testing link: {link}")
    page_metadata, error = get_page_metadata(link)
    if error:
        return {'link': link, 'status': 'error', 'error': error}
    else:
        return {'link': link, 'status': 'success', **page_metadata}

def test_links_concurrently(search_results_list):
    results_list = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_link, item): item for item in search_results_list}
        for future in as_completed(futures):
            result = future.result()
            results_list.append(result)
    return results_list

def generate_report(test_results, query_topic):
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
    timestamped_csv = timestamped_filename("links_scrape_report.csv")
    with open(timestamped_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'status', 'title', 'description', 'keywords', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in test_results:
            writer.writerow(result)
    
    return timestamped_csv

def main():
    # Create a Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Prompt the user for the search query using Tkinter
    query = simpledialog.askstring("Input", "Please enter the search query topic:")

    # Check if the user provided a query
    if query:
        loader = GoogleSearchLoader(query=query)
        
        # # Load and scroll through the Google search resultset, then save the HTML content from the Google Search Result Page
        # html_content = loader.load_and_scroll()
        # html_filename = loader.save_html(html_content)
        # print(f"HTML content saved to {html_filename}")

        # # Parse the HTML content FILE to extract search results in JSON format
        # search_results_list = loader.parse_items(html_content)
        # print(f"Extracted {len(search_results_list)} items.")

        search_results_list = []

        # Ensure we have at least 100 unique links (JSON objects from search_results_list)
        # `search_results_list` is a JSON array of objects with keys: 'title', 'link', 'snippet'
        # In Python, the search_results_list is a list of dictionaries.
        print(f"Starting to collect links...")
        if len(search_results_list) < 100:
            while len(search_results_list) < 100:
                # # Load and scroll through the Google search resultset, then save the HTML content from the Google Search Result Page
                html_content = loader.load_and_scroll()
                search_results_list.extend(loader.parse_items(html_content))
                search_results_list = list({item['link']:item for item in search_results_list if item['link']}.values())
                print(f"Collected {len(search_results_list)} links so far...")

        html_filename = loader.save_html(html_content)
        print(f"HTML content saved to {html_filename}")

        # Save the parsed search_results_LIST to a JSON file named "json_filename"
        json_filename = loader.save_results_to_json(search_results_list[:100])  # Ensure we have at most 100 links
        print(f"Parsed search results have been saved to {json_filename}")

        # Load the parsed search results from the JSON file
        with open(json_filename, 'r', encoding='utf-8') as f:
            search_results_list = json.load(f)

        # Test the links concurrently and save the results
        test_results = test_links_concurrently(search_results_list)
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
