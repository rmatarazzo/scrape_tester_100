
This program does a Google search to search, retrieve, and scrape approximately 100 search link results.  Then each link is tested using link_test() to verify that it is a valid link.  Right now it is using multithreading and threads do not terminate properly and memory leaks occur.  It appears that ThreadPoolExecutor is not terminating the webdriver that is created when the get_page_metadata() function is called to perform test_link().  The webdriver is opening a browser instance either in headless mode or non-headless mode, but the webdriver instance is not terminated properly.  This appears to be causing a runaway condition where leftover threads build up and eat up memory.  

What is the best way to solve this problem?  We need to guarantee that each webdriver browser instance closes and memory, threads, and processes are reclaimed after each link_test is done.  

Please analyze tester3.py and provide suggestions to fix it.

How can I 

I need to modify the selected code to properly use a subprocess whenever a webdriver is called.  Each 