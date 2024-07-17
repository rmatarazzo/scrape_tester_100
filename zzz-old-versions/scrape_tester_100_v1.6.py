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
import requests
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
        """Load search results and scroll until at least 100 items or no new items are found."""
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
                next_button = driver.find_element(By.ID, 'pnnext')
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                time.sleep(2)
            except Exception:
                break

        driver.quit()
        return collected_html

    def parse_items(self, html):
        """Parse the search result items from the HTML content."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        for item in soup.select('div.g'):
            title = item.select_one('h3').text if item.select_one('h3') else ''
            link = item.select_one('a')['href'] if item.select_one('a') else ''
            snippet = item.select_one('.IsZvec').text if item.select_one('.IsZvec') else ''
            results.append({'title': title, 'link': link, 'snippet': snippet})

        return results

    def save_html(self, html):
        """Save the HTML content to a file."""
        filename = timestamped_filename('google_search_results.html')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        return filename

    def save_results_to_json(self, results):
        """Save the search results to a JSON file."""
        filename = timestamped_filename('parsed_search_results.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        return filename

def test_link(link):
    """Test a single link by making a HEAD request."""
    try:
        response = requests.head(link, timeout=5)
        return {'link': link, 'status': response.status_code, 'reason': response.reason}
    except requests.RequestException as e:
        return {'link': link, 'status': 'error', 'reason': str(e)}

def test_links_concurrently(links):
    """Test multiple links concurrently."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_link, link['link']) for link in links]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    return results

def generate_report(results, query):
    """Generate a text report from the test results."""
    report = f"Scrape Test Report for Query: {query}\n\n"
    for result in results:
        report += f"{result['link']} - {result['status']} - {result['reason']}\n"
    return report

def save_report_to_csv(results, query):
    """Save the report to a CSV file."""
    filename = timestamped_filename('links_scrape_report.csv')
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'status', 'reason']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    return filename

def main():
    # Use Streamlit to input the search query
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
