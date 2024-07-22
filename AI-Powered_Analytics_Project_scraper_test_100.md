# AI-Powered Data Science & Analytics Project Definition (Template):

Created By: Rich Lysakowski
Updated On: 2024.05.20
Shared Location:  G:\Shared drives\AI-Powered Data Analytics Training\01_Projects_Core\!0_Project_Templates\
    00-Project-Solution-Description-Section-Template-YAMLv-2024.04.10.txt

## Project Name: a descriptive title (should be "catchy" for marketing purposes)
Scrape Tester 100


## Project and Work Product Description:  (should be 1 CONCISE paragraph, 3-7 sentences)
	• Answer "This project / work product (solution) fills these gaps... "
    
	Identify websites suitable for web scraping automatically.
	User is prompted to enter a topic that will be used to generate a list of up to 100 relevant websites.
	The program builds a list of their links.
	Each link is tested for web scraping capabilities.
	The program generates a report for the user that identifies which websites were successfully scraped and which ones failed along with corresponding error codes.
			
    • Main goals and problem(s) it solves.
	
	Provide a list of websites that can be used for a topic of interest that are suitable for web scraping.
	Saves time by filtering potential websites for a project and identifying those suitable for web scraping and data extraction.
	
	• Problem and Solution Workflow Diagrams (2 flowcharts "AS-IS" and "TO-BE")
	
	AS-IS Workflow:
	Textual Description:

	User Input: User enters a topic for web scraping.
	Manual Search: User manually searches and identifies websites related to the entered topic, up to 100 websites.
	Manual Link Compilation: User manually compiles a list of links from the identified websites.
	Manual Capability Check: User manually checks each link to determine its potential for successful web scraping.
	Manual Report Generation: User manually generates a report listing websites successfully scraped and those that failed, with error details.	


	TO-BE Workflow:
	Textual Description:

Import Libraries:
	Import necessary libraries including os, json, time, datetime, quote_plus from urllib.parse, BeautifulSoup, selenium modules, ThreadPoolExecutor from concurrent.futures, streamlit, and csv.

Helper Function:
	timestamped_filename(base_filename): Generates a timestamped filename.

Class Definition: GoogleSearchLoader:
	Initialization:
		__init__(self, query): Initializes the object with a search query.
	Methods:
		load_and_scroll(self): Loads Google search results and scrolls to load more results until 100 items are found or no new items are loaded.
		save_html(self, html_content, base_filename="google_search_results.html"): Saves the HTML content to a timestamped file.
		save_results_to_json(self, results, base_filename="parsed_search_results.json"): Saves parsed search results to a timestamped JSON file.
		parse_items(self, html_content): Parses search items from HTML content using BeautifulSoup.
	
Function Definitions:
	get_page_metadata(link): Retrieves metadata (title, description, keywords) from a webpage using Selenium.
	test_link(link_info): Tests a single link by retrieving its metadata and returning a status.
	test_links_concurrently(search_results): Tests a list of links concurrently and collects the results.
	generate_report(test_results, query_topic): Generates a text-based report summarizing the test results.
	save_report_to_csv(test_results, query_topic): Saves the test results to a CSV file with a timestamped filename.
	
Main Function:
	Orchestrates the scraping and testing workflow using Streamlit.
	Takes user input for the search query.
	Initializes GoogleSearchLoader.
	Loads and scrolls through the search results.
	Saves the HTML content.
	Parses the HTML content to extract search results.
	Ensures at least 100 unique links are collected.
	Saves the parsed search results to a JSON file.
	Loads the parsed search results from the JSON file.
	Tests the links concurrently and saves the results.
	Generates and saves the report.
	Saves the report to a CSV file.
	
    "A problem clearly stated is a problem half-solved." - Dorothea Brande :


## Description of Solution:  (should be CONCISE, 3-7 sentences)

	The solution automates the identification and evaluation of websites suitable for web scraping based on a user-provided topic. Upon receiving the topic, the program automatically searches and compiles a list of up to 100 relevant websites. Each website is then subjected to an automated test scrape to assess its suitability for data extraction. The program handles any errors encountered during the testing phase and generates a comprehensive report, detailing which websites were successfully scraped and which ones failed, along with corresponding error codes. This automation significantly reduces manual effort and increases the efficiency and accuracy of identifying scrappable websites.
	
	• Software functions for solving problem(s) step by step.
	
Step-by-Step Breakdown of Functions

1. Helper Function: timestamped_filename
	Purpose: Generates a filename with a timestamp to uniquely identify the file.
	Parameters:
		base_filename (str): The base name of the file without the extension.
	Returns:
		str: The timestamped filename including the original base name and extension.
	
2. Class: GoogleSearchLoader
	Purpose: Loads and processes Google search results.
	Initialization
	Parameters: 
		query (str): The search query string.

	Method: load_and_scroll
	Purpose: Loads search results and scrolls until at least 100 items or no new items are found.
	Returns:
		str: The HTML content of the loaded pages.
		
	Method: save_html
	Purpose: Saves the HTML content to a timestamped file.
	Parameters:
		html_content (str): The HTML content to save.
		base_filename (str): The base name of the file without the extension.
	Returns:
		str: The timestamped filename of the saved HTML file.
		
	Method: save_results_to_json
	Purpose: Saves the parsed results to a timestamped JSON file.
	Parameters:
		results (list): The list of parsed results.
		base_filename (str): The base name of the file without the extension.
	Returns:
		str: The path to the saved JSON file.
		
	Method: parse_items
	Purpose: Parses search items from HTML content using BeautifulSoup.
	Parameters:
		html_content (str): The HTML content to parse.
	Returns:
		list: A list of dictionaries containing parsed search items.
		
3. Function: get_page_metadata
	Purpose: Retrieves metadata (title, description, keywords) from a webpage using Selenium.
	Parameters:
		link (str): The URL of the webpage.
	Returns:
		tuple: A tuple containing the metadata dictionary and any error message.
		
4. Function: test_link
	Purpose: Tests a single link by retrieving its metadata and returning a status.
	Parameters:
		link_info (dict): A dictionary containing the link and optional error handling.
	Returns:
		dict: A dictionary with the link status and optionally error details.
		
5. Function: test_links_concurrently
	Purpose: Tests a list of links concurrently and collects the results.
	Parameters:
		search_results (list): A list of dictionaries representing links to test.
	Returns:
		list: A list of dictionaries containing the test results for each link.
		
6. Function: generate_report
	Purpose: Generates a text-based report summarizing the test results.
	Parameters:
		test_results (list): A list of dictionaries containing the test results.
		query_topic (str): The search query topic used for testing.
	Returns:
		str: A formatted string representing the report.
		
7. Function: save_report_to_csv
	Purpose: Saves the test results to a CSV file with a timestamped filename.
	Parameters:
		test_results (list): A list of dictionaries containing the test results.
		query_topic (str): The search query topic used for testing.
	Returns:
		str: The path to the saved CSV file.
		
8. Main Function
	Purpose: Orchestrates the entire process using Streamlit for user interaction.
	Steps:
		Collects user input for the search query.
		Initializes GoogleSearchLoader with the query.
		Loads and scrolls through the search results.
		Saves the HTML content.
		Parses the HTML content to extract search results.
		Ensures at least 100 unique links are collected.
		Saves the parsed search results to a JSON file.
		Loads the parsed search results from the JSON file.
		Tests the links concurrently and saves the results.
		Generates and saves the report.
		Saves the report to a CSV file.
		

Summary of Steps and Functions:

1. Helper Function: timestamped_filename
	Purpose: Generates a filename with a timestamp to ensure uniqueness.
	Steps:
		Get the current timestamp.
		Split the base filename into name and extension.
		Return the combined filename with the timestamp.
2. Class: GoogleSearchLoader
		Purpose: Handles the loading and processing of Google search results.
		Initialization (__init__):
		Store the search query.
Method: load_and_scroll:
	Initialize a headless Selenium Chrome WebDriver.
	Load the Google search page with the query.
	Scroll and collect HTML content until at least 100 results are found or no new items are available.
	Return the collected HTML content.
Method: save_html:
	Save the HTML content to a timestamped file.
	Return the filename.
Method: save_results_to_json:
	Save the parsed results to a timestamped JSON file.
	Return the filename.
Method: parse_items:
	Parse search items from the HTML content using BeautifulSoup.
	Extract title, link, and snippet for each item.
	Return a list of dictionaries with the parsed items.
3. Function: get_page_metadata
	Purpose: Retrieve metadata (title, description, keywords) from a webpage.
	Steps:
		Initialize a headless Selenium Chrome WebDriver.
		Load the webpage.
		Extract title, description, and keywords.
		Return the metadata and any error message.
4. Function: test_link
	Purpose: Test a single link by retrieving its metadata.
	Steps:
		Call get_page_metadata for the link.
		Return the link status and metadata or error.
5. Function: test_links_concurrently
	Purpose: Test a list of links concurrently.
	Steps:
		Use a ThreadPoolExecutor to test links in parallel.
		Collect and return the results.
6. Function: generate_report
	Purpose: Generate a text-based report summarizing the test results.
	Steps:
		Count successful and error results.
		Format the results into a report string.
		Return the report.
7. Function: save_report_to_csv
	Purpose: Save the test results to a CSV file.
	Steps:
		Create a timestamped CSV file.
		Write the test results to the CSV file.
		Return the filename.
8. Main Function
	Purpose: Orchestrate the entire process using Streamlit for user interaction.
	Steps:
		Collect user input for the search query.
		Initialize GoogleSearchLoader with the query.
		Load and scroll through the search results.
		Save the HTML content.
		Parse the HTML content to extract search results.
		Ensure at least 100 unique links are collected.
		Save the parsed search results to a JSON file.
		Load the parsed search results from the JSON file.
		Test the links concurrently and save the results.
		Generate and save the report.
		Save the report to a CSV file.
	
	• Workflow diagram of future ("TO-BE") state (improved processes from your solution).
	• "Minimum Viable Product" (MVP) 1.0 delivered.  (V1.x delivered beyond MVP V1.0?)
	• Later MVP, i.e., v2, v3, vN+ functionality to be delivered? 
    • Additional requirements, Graphical User Interfaces (GUI), usability, etc. for later versions
    
	Implementation Packages:
	Selenium - for web browser automation
	Selenium WebDriver Manager (get latest selenium version that contains webdriver Manager)
	Faker - for generating a random browser user agent
	
	Implementation Workflow Considerations:
	
	
	
### Solution Design (high-level):
    • Architecture Design Diagram (Client-Server-DB Block Diagram?) 
    • User Interface Mockup (wireframe?)

### Solution Code Description (low-level design): 
	• Describe code (to help users understand it.)
	• Hyperlinks to actual complete code  

### Actual Working Product Code: 
    Packages, modules, functions, documentation
		packages that are required (from other people)
		custom packages, modules, classes, functions that you created
    
## Application Instructions:

    • Step-by-step instructions for USERS of your Application:
        Instructions for other people to install, set-up, and use your software:
        Everything needed to get your solution working.   
            Software packages and tools
            Configuration, data sets, URLs, input and output folder structure, etc. 
        
    • Additional Important Guidelines for Product Usability (for others to use your work products):
	
## Future Enhancements:
	Later MVPs, i.e., v2, v3, vn

## Lessons Learned:
	Any skills or knowledge acquired by doing the projects
	Hard and software skills:
		Coding, Tools, packages
		Software Engineering Specification and any other technical hands-on work
		Project Management, communication, collaboration, strategy, delivery
		Presentation