import pandas as pd

# Step 1: Read the content of the text file
file_path = 'C:/Users/rmata/Desktop/00_PythonWIP/Projects/scrape_tester_100/links_scrape_report_20240702_204125.txt'

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
df.head()

# Output the formatted DataFrame
print(df)
