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
import pandas as pd

output_dir = 'data_output_files'
os.makedirs(output_dir, exist_ok=True)

drivers = []
drivers_pids = []  # Store PIDs of WebDriver instances

def timestamped_filename(base_filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(base_filename)
    return f"{filename}_{timestamp}{ext}"

class GoogleSearchLoader:
    def __init__(self, query, pid_callback=None):
        self.query = query
        self.pid_callback = pid_callback

    def load_and_scroll(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        if self.pid_callback:
            self.pid_callback(driver.service.process.pid)

        try:
            driver.get(f"https://www.google.com/search?q={quote_plus(self.query)}")
            num_results = 0
            collected_html = ""
            wait = WebDriverWait(driver, 10)

            while num_results < 100:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.g')))

                search_items = driver.find_elements(By.CSS_SELECTOR, 'div.g')
                num_results += len(search_items)
                collected_html += driver.page_source

                if num_results >= 100:
                    break

                try:
                    next_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a#pnnext'))
                    )
                    next_button.click()
                    time.sleep(2)
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
            driver.quit()

    def save_html(self, html_content, base_filename="Google_search_results.html"):
        soup = BeautifulSoup(html_content, 'html.parser')
        pretty_html = soup.prettify()

        timestamped_file = timestamped_filename(base_filename)
        
        with open(timestamped_file, 'w', encoding='utf-8') as file:
            file.write(pretty_html)
        
        return timestamped_file    

    def save_results_to_json(self, results, base_filename="parsed_Google_search_results.json"):
        json_filename = timestamped_filename(base_filename)
        with open(json_filename, "w", encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        return json_filename 

    def parse_items(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        search_items = soup.select('div.g')
        for item in search_items:
            title_div = item.select_one('h3')
            title = title_div.text if title_div else "No title"
            link_tag = item.select_one('a')
            link = link_tag['href'] if link_tag and 'link' in link_tag.attrs else None
            snippet_div = item.select_one('div.kb0PBd')
            snippet = snippet_div.text if snippet_div else "No snippet available"
            if link:
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        return results 

def get_page_metadata(link, pid_callback=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    if pid_callback:
        pid_callback(driver.service.process.pid)

    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        title = driver.title
        
        metadata = {
            "title": title,
            "description": "",
            "keywords": ""
        }
        
        try:
            description_element = driver.find_element(By.XPATH, "//meta[@name='description']")
            metadata['description'] = description_element.get_attribute('content') if description_element else "No description found"
        except Exception:
            metadata['description'] = "Description meta tag not found."
        
        try:
            keywords_element = driver.find_element(By.XPATH, "//meta[@name='keywords']")
            metadata['keywords'] = keywords_element.get_attribute('content') if keywords_element else "No keywords found"
        except Exception:
            metadata['keywords'] = "Keywords meta tag not found."

        return metadata, None 
    except Exception as e:
        return None, str(e)
    finally:
        if driver:
            driver.quit()

def test_link(link_info):
    link = link_info['link']
    metadata, error = get_page_metadata(link)
    if error:
        return {'link': link, 'status': 'error', 'error': error}
    else:
        return {'link': link, 'status': 'success', **metadata}

def test_links_concurrently(search_results):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_link, item): item for item in search_results}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    return results 

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
    st.title('Google Search Scrape Test')
    query = st.text_input('Please enter the search query topic:')
    
    if query:
        if st.button('Run Scrape Test'):
            store_pid(None)  # Store a None value to indicate the start of WebDriver instances
            
            loader = GoogleSearchLoader(query=query, pid_callback=store_pid)
            html_content = loader.load_and_scroll()
            html_filename = loader.save_html(html_content)
            st.write(f"HTML content saved to {html_filename}")

            search_results = loader.parse_items(html_content)
            st.write(f"Extracted {len(search_results)} items.")

            if len(search_results) < 100:
                st.write(f"Collected only {len(search_results)} links, retrying to get more...")
                while len(search_results) < 100:
                    html_content = loader.load_and_scroll()
                    search_results.extend(loader.parse_items(html_content))
                    search_results = list({item['link']: item for item in search_results if item['link']}.values())
                    st.write(f"Collected {len(search_results)} links so far...")

            json_filename = loader.save_results_to_json(search_results[:100])
            st.write(f"Parsed search results saved to {json_filename}")

            with open(json_filename, 'r', encoding='utf-8') as f:
                search_results = json.load(f)

            test_results = test_links_concurrently(search_results)
            output_filename = timestamped_filename('parsed_Google_links_scrape_test.json')
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, ensure_ascii=False, indent=4)
            st.write(f"Test results saved to {output_filename}")

            report = generate_report(test_results, query)
            report_filename = timestamped_filename('Google_links_scrape_report.txt')

            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            st.write(f"Report saved to {report_filename}")

            csv_filename = save_report_to_csv(test_results, query)
            st.write(f"CSV report saved to {csv_filename}")

            # Ensure all WebDriver instances are closed
            for pid in drivers_pids:
                for driver in drivers:
                    if driver.service.process.pid == pid:
                        driver.quit()

            drivers_pids.clear()  # Clear the list to prepare for the next run

if __name__ == "__main__":
    try:
        main()
    finally:
        # Ensure all WebDriver instances are closed
        for pid in drivers_pids:
            for driver in drivers:
                if driver.service.process.pid == pid:
                    driver.quit()