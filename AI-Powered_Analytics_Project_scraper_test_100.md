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

	1. User Input: User is prompted and provides a topic for web scraping tests.
	2. Automated Website Identification: Program uses requests, beautifulsoup, and langchain to automatically search Google to identify 100 websites relevant to the provided topic.
	3. Automated Link Compilation: Program automatically compiles a list of 100 links from the Google search identified websites.
	4. Test Web Scraping Capability: Program performs and automated test scrape for each identified link to determine if it can be successfully scraped.
	5. Error Handling: Program handles errors encountered during testing and scraping, and then categorizes them with appropriate error codes.
	6. Generate Comprehensive Report: Program will then produce a detailed report listing the 100 websites that were successfully scraped and those that failed, including error details.
	
    "A problem clearly stated is a problem half-solved." - Dorothea Brande :


## Description of Solution:  (should be CONCISE, 3-7 sentences)

	The solution automates the identification and evaluation of websites suitable for web scraping based on a user-provided topic. Upon receiving the topic, the program automatically searches and compiles a list of up to 100 relevant websites. Each website is then subjected to an automated test scrape to assess its suitability for data extraction. The program handles any errors encountered during the testing phase and generates a comprehensive report, detailing which websites were successfully scraped and which ones failed, along with corresponding error codes. This automation significantly reduces manual effort and increases the efficiency and accuracy of identifying scrappable websites.
	
	• Software functions for solving problem(s) step by step.
	
User Input:
Function to prompt the user for a topic.
GUI-based input or command-line input can be utilized.

Automated Website Identification:
Function to perform a Google search using the provided topic.
Use requests to fetch search results and BeautifulSoup to parse the HTML content.
Use LangChain to manage and organize the search results.

Automated Link Compilation:
Function to extract links from the Google search results.
Compile a list of the top 100 links.

Test Web Scraping Capability:
Function to attempt scraping each identified link.
Check for the presence of relevant content and handle different content structures.
Use BeautifulSoup for parsing the HTML content of each link.

Error Handling:
Function to handle and log errors encountered during the scraping process.
Categorize errors with appropriate error codes (e.g., 404 Not Found, 403 Forbidden, 500 Internal Server Error).

Generate Comprehensive Report:
Function to compile the results into a detailed report.
List websites that were successfully scraped and those that failed, including error details.
Output the report in a user-friendly format (e.g., CSV, JSON, or a formatted text file).



Summary of Steps and Functions:
User Input:

get_user_input(): Prompts the user for a search topic.
Automated Website Identification:

search_google(query): Performs a Google search and fetches the search results page.
Automated Link Compilation:

extract_links(html): Extracts and compiles the top 100 links from the search results.
Test Web Scraping Capability:

test_scraping(link): Tests each link to determine if it can be successfully scraped.
Error Handling:

Integrated into test_scraping(link): Logs errors and categorizes them with appropriate error codes.
Generate Comprehensive Report:

generate_report(results): Produces a detailed report of the scraping results.


	Get User Input:
	Function: get_user_topic()
	Description: Prompts the user to enter a topic for web scraping.
	
	Search for Relevant Websites:
	Function: search_websites(topic)
	Description: Searches the internet for websites related to the given topic and compiles a list of up to 100 relevant sites.
	
	Compile List of Links:
	Function: compile_links(websites)
	Description: Extracts and compiles links from the list of identified websites.
	
	Test Web Scraping Capability:
	Function: test_scraping(link)
	Description: Performs a test scrape on each link to determine if it can be successfully scraped.
	
	Error Handling:
	Function: handle_errors(error)
	Description: Categorizes and logs errors encountered during the scraping tests, assigning appropriate error codes.
	
	Generate Report:
	Function: generate_report(successful_links, failed_links)
	Description: Generates a report listing the websites that were successfully scraped and those that failed, including detailed error codes.
	
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
    Functions, modules, packages, documentation 
    
## Application Instructions:

    • Step-by-step instructions for USERS of your Application:
        Instructions for other people to install, set-up, and use your software:
        Everything needed to get your solution working.   
            Software packages and tools
            Configuration, data sets, URLs, input and output folder structure, etc. 
        
    • Additional Important Guidelines for Product Usability (for others to use your work products):


