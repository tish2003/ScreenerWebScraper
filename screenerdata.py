import requests
from lxml import html
import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup

# Set up the Edge WebDriver for Peer Comparison table
driver = webdriver.Edge()
url = "https://www.screener.in/company/RELIANCE/consolidated"
driver.get(url)
time.sleep(5)  # Allow time for the page to load

# Get the page source and parse it with lxml for Peer Comparison table
page_source = driver.page_source
tree = html.fromstring(page_source)

# Prepare a list to hold all data
all_data = []

# Add company title using requests and BeautifulSoup
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
title = soup.find('h1', {'class': 'h2 shrink-text'}).text.strip()
all_data.append(["Company Name", title])  # Add the title to all_data
all_data.append([])  # Blank line for separation

# Extract Metrics section
metrics = soup.find_all('li', {'class': 'flex flex-space-between'})
all_data.append(["Metrics"])
for metric in metrics:
    name = metric.find('span', {'class': 'name'}).text.strip()
    value_element = metric.find('span', {'class': 'nowrap value'})
    if value_element:
        symbol = value_element.find('span', {'class': 'symbol'})
        number = value_element.find('span', {'class': 'number'}).text.strip()
        suffix = value_element.text.strip().replace(number, "").strip()
        value = f"{symbol.text.strip()} {number} {suffix}" if symbol else f"{number} {suffix}"
        all_data.append([name, value])
all_data.append([])  # Blank line for separation

# Extract Quarterly Results Table
quarterly_table = soup.find('table', {'class': 'data-table'})
if quarterly_table:
    headers = [header.text.strip() for header in quarterly_table.find_all('th')]
    rows = [[cell.text.strip() for cell in row.find_all('td')] for row in quarterly_table.find_all('tr')[1:]]
    all_data.append(["Quarterly Results Table"])
    all_data.append(headers)
    all_data.extend(rows)
all_data.append([])  # Blank line for separation

# Extract Profit and Loss Table
pl_table = soup.find('section', {'id': 'profit-loss'})
if pl_table:
    headers = [th.get_text(strip=True) for th in pl_table.find('thead').find_all('th')]
    rows = [[col.get_text(strip=True) for col in row.find_all(['td', 'th'])] for row in pl_table.find('tbody').find_all('tr')]
    all_data.append(["Profit & Loss Table"])
    all_data.append(headers)
    all_data.extend(rows)
all_data.append([])  # Blank line for separation

# Function to add data with headers to the all_data list
def add_table_data(label, headers, rows):
    all_data.append([label])  # Add table label
    all_data.append(headers)  # Add headers
    all_data.extend(rows)     # Add rows
    all_data.append([])       # Blank line between tables for readability

# Extract Peer Comparison table using WebDriver
peer_table = tree.xpath('//*[@id="peers-table-placeholder"]/div[3]/table')
if peer_table:
    headers = [header.strip() for header in peer_table[0].xpath(".//thead//th/text()")]
    rows = [
        [data.strip() for data in row.xpath(".//td/text()")]
        for row in peer_table[0].xpath(".//tbody//tr")
    ]
    add_table_data("Peer Comparison Table", headers, rows)

# Close the WebDriver
driver.quit()

# Extract Balance Sheet and Cash Flow tables using requests and lxml
tree = html.fromstring(response.content)
tables = {
    "Balance Sheet": "//section[@id='balance-sheet']//table",
    "Cash Flow": "//section[@id='cash-flow']//table"
}

for table_name, xpath in tables.items():
    table = tree.xpath(xpath)
    if table:
        headers = [header.strip() for header in table[0].xpath(".//thead//th/text()")]
        rows = [
            [data.strip() for data in row.xpath(".//td/text()")]
            for row in table[0].xpath(".//tbody//tr")
        ]
        add_table_data(f"{table_name} Table", headers, rows)

# Save all data to a CSV file
with open("financial_data.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(all_data)

print("Data saved to financial_data.csv successfully.")
