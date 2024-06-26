import os
import json
import time
from datetime import datetime
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import simpledialog

def timestamped_filename(base_filename):
    """Generate a filename with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"

class GoogleSearchLoader:
    def __init__(self, query):
        self.query = query

    def load_and_scroll(self):
        """Load search results and scroll until at least 100 items or no new items are found."""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(f"https://www.google.com/search?q={quote_plus(self.query)}")

        num_results = 0
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while num_results < 100:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(20)  # Increased delay to allow more content to load
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a#pnnext')
                    next_button.click()
                    time.sleep(20)  # Wait for the next page to load
                    last_height = driver.execute_script("return document.body.scrollHeight")
                except Exception:
                    try:
                        more_results_button = driver.find_element(By.XPATH, '//a[contains(., "More results")]')
                        more_results_button.click()
                        time.sleep(20)  # Wait for more results to load
                        last_height = driver.execute_script("return document.body.scrollHeight")
                    except Exception:
                        print("No more pages or unable to load more results.")
                        break  # No new items or next/more results button was not found
            else:
                last_height = new_height
            
            search_items = driver.find_elements(By.CSS_SELECTOR, 'div.g')
            num_results = len(search_items)
        
        html_content = driver.page_source
        driver.quit()
        return html_content

    def parse_items(self, html_content):
        """Parse search items from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        search_items = soup.select('div.g')  # Adjust the selector as needed
        for item in search_items:
            title_div = item.select_one('h3')
            title = title_div.text if title_div else "No title"
            link_tag = item.select_one('a')
            link = link_tag['href'] if link_tag else None
            snippet_div = item.select_one('div.kb0PBd')
            snippet = snippet_div.text if snippet_div else "No snippet available"
            if link:
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        return results

    def save_html(self, html_content, base_filename="google_search_results.html"):
        """Save the HTML content to a timestamped file."""
        timestamped_file = timestamped_filename(base_filename)
        with open(timestamped_file, 'w', encoding='utf-8') as file:
            file.write(html_content)
        return timestamped_file

    def save_results_to_json(self, results, base_filename="parsed_search_results.json"):
        """Save the parsed results to a timestamped JSON file."""
        json_filename = timestamped_filename(base_filename)
        with open(json_filename, "w", encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        return json_filename

def get_page_title(link):
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(link)
        title = driver.title
        driver.quit()
        return title, None
    except Exception as e:
        return None, str(e)

def test_link(link_info):
    link = link_info['link']
    title, error = get_page_title(link)
    if error:
        return {'link': link, 'status': 'error', 'error': error}
    else:
        return {'link': link, 'status': 'success', 'title': title}

def test_links_concurrently(search_results):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_link, item): item for item in search_results}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    return results

def generate_report(test_results):
    success_count = sum(1 for result in test_results if result['status'] == 'success')
    error_count = len(test_results) - success_count

    report_lines = [
        "Link Scrape Test Report",
        f"Total Links Tested: {len(test_results)}",
        f"Total Successes: {success_count}",
        f"Total Errors: {error_count}",
        "",
        "Details:"
    ]

    for result in test_results:
        if result['status'] == 'success':
            report_lines.append(f"SUCCESS: {result['link']} - Title: {result['title']}")
        else:
            report_lines.append(f"ERROR: {result['link']} - Error: {result['error']}")

    return "\n".join(report_lines)

def main():
    # Create a Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Prompt the user for the search query using Tkinter
    query = simpledialog.askstring("Input", "Please enter the search query topic:")

    # Check if the user provided a query
    if query:
        loader = GoogleSearchLoader(query=query)
        
        # Load and scroll through the search results, then save the HTML content
        html_content = loader.load_and_scroll()
        html_filename = loader.save_html(html_content)
        print(f"HTML content saved to {html_filename}")

        # Parse the HTML content to extract search results
        search_results = loader.parse_items(html_content)
        print(f"Extracted {len(search_results)} items.")

        # Save the parsed search results to a JSON file
        json_filename = loader.save_results_to_json(search_results)
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
        report = generate_report(test_results)
        report_filename = timestamped_filename('links_scrape_report.txt')
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {report_filename}")

    else:
        print("No query provided. Exiting.")

if __name__ == "__main__":
    main()
