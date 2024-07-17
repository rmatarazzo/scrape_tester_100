import pandas as pd
import os

# Step 1: Read the content of the text file
file_path = 'C:/Users/rmata/Desktop/00_PythonWIP/Projects/scrape_tester_100/links_scrape_report_20240702_204125.txt'

# Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")

with open(file_path, 'r') as file:
    lines = file.readlines()

# Step 2: Parse the header information
header_info = {}
header_info['Search Query'] = lines[1].split(': ')[1].strip()
header_info['Total Links Tested'] = int(lines[2].split(': ')[1].strip())
header_info['Total Successes'] = int(lines[3].split(': ')[1].strip())
header_info['Total Errors'] = int(lines[4].split(': ')[1].strip())

# Step 3: Parse the details of each success and error entry
details = []
for line in lines[7:]:
    if line.startswith("SUCCESS:") or line.startswith("ERROR:"):
        parts = line.split(' - Metadata: ')
        status, url = parts[0].split(': ', 1)
        metadata = parts[1].strip() if len(parts) > 1 else ''
        details.append([status, url, metadata])

# Step 4: Create a pandas DataFrame from the parsed data
df = pd.DataFrame(details, columns=['Status', 'URL', 'Metadata'])

# Step 5: Format the DataFrame for readability
df['Metadata'] = df['Metadata'].apply(lambda x: x.replace("{", "").replace("}", "").replace("'", "").replace(",", "\n"))

# Add header information
header = [
    "Link Scrape Test Report",
    f"Search Query: {header_info['Search Query']}",
    f"Total Links Tested: {header_info['Total Links Tested']}",
    f"Total Successes: {header_info['Total Successes']}",
    f"Total Errors: {header_info['Total Errors']}",
    ""
]
header_str = "\n".join(header)

# Save the DataFrame to a CSV file
output_csv_path = 'C:/Users/rmata/Desktop/00_PythonWIP/Projects/scrape_tester_100/links_scrape_report_formatted.csv'
try:
    with open(output_csv_path, 'w') as f:
        f.write(header_str + "\n")
        df.to_csv(f, index=False)
    print(f"File saved successfully to {output_csv_path}")
except Exception as e:
    print(f"An error occurred while saving the file: {e}")

# Display the DataFrame in a more readable format
pd.set_option('display.max_colwidth', None)
print(header_str)
print(df)
