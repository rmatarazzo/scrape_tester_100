
BEST PRACTICES PROMPT

PROMPT PREFIX: 

Use the code in the editor VERBATIM, and make sure you include all existing code in your answer. Rewrite the entire file using the instructions.  NEVER return fragments or snippets when I ask you to rewrite the entire function.

PROMPT
Rewrite the webscraper code selected in the editor to do the following:

For each run of scrape_tester_100_v1.py, save each page to an HTML file into a folder named "run_{datetime}" where datetime is when the folder is created.

Save each page to a file as soon as the browser visits the page. Use a filename name "{search_query}page{N}.html, where search_query is the search terms joined with an underscore, and N is sequential page number.


PROMPT to improve page loading.  

Use  Webdriver Wait to wait for the current page to load.  


Get run folder working
save each file during a run
parse each file offline

improve selenium operations using Webdrdriver Wait

[OPTIONAL Create your own output page of scraped results (markdown)]

parse each HTML into your desired JSON or text, or HTML

VSCode 
UPdate VSCode to fix missing sidebar and file explorer.
VSCode is not showing file explorer