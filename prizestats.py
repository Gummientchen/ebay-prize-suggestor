import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.parse import quote_plus
import matplotlib
import matplotlib.pyplot as plt

# get average of a list
def Average(lst): 
    return sum(lst) / len(lst)

# tests if a string is a number/float
def is_number_tryexcept(s):
    """ Returns True if string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False




# ask user for search query
search_query = input("Search: ")
search_query = quote_plus(search_query)

URL = "https://www.ebay.ch/sch/i.html?_from=R40&_nkw="+search_query+"&_sacat=0&LH_TitleDesc=0&_fsrp=1&LH_Complete=1&_ipg=240&LH_Sold=1&_blrs=spell_auto_correct&rt=nc&LH_ItemCondition=3000"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

# remove all results after "Ergebnisse für weniger Suchbegriffe"
try:
    target = soup.find("span", class_="section-notice__main")
    for e in target.find_all_next():
        e.clear()
except:
    pass

# get items
results = soup.find_all("div", class_="s-item__wrapper")

# get condition and price
prices = []
for item in results:
    try:
        secondary_info = item.find("span", class_="SECONDARY_INFO").text
    except:
        secondary_info = ""

    try:
        item_price = item.find("span", class_="s-item__price").text
    except:
        item_price = ""

    if secondary_info == "Gebraucht":
        price = item_price.replace(".","")
        price = price.replace(",",".")
        price = price.replace("CHF ","")
        
        if is_number_tryexcept(price):
            prices.append(float(price))

# cancel if not enough results are available
if len(prices) < 3:
    print("not enough sold products found...")
    exit()

# prices = sorted(prices, reverse=True)

# calculate values for filtering out items which deviate too much
Q1 = np.percentile(prices, 33, method='midpoint')
Q3 = np.percentile(prices, 67, method='midpoint')
IQR = Q3 - Q1

upper=Q3+1.25*IQR
lower=Q1-1.25*IQR

# filter list
filtered_prices = []
for price in prices:
    if price > lower and price < upper:
        filtered_prices.append(price)

# sorted = sorted(filtered_prices, reverse=True)

# print(*sorted, sep="\n")

# calculate average
average_price = Average(filtered_prices)
max_price = max(filtered_prices)
min_price = min(filtered_prices)

# format output
line_width = 35

string_average_price = '{:.2f}'.format(average_price)+" CHF"
string_max_price = '{:.2f}'.format(max_price)+" CHF"
string_min_price = '{:.2f}'.format(min_price)+" CHF"

title_average = "Average Sold Price:"
title_max_price = "Upper Bound:"
title_min_price = "Lower Bound:"

output_average = title_average+string_average_price.rjust(line_width-len(title_average)," ")
output_max_price = title_max_price+string_max_price.rjust(line_width-len(title_max_price)," ")
output_min_price = title_min_price+string_min_price.rjust(line_width-len(title_min_price)," ")

# output results
print("")
print(output_max_price)
print(output_min_price)
print(output_average)
print("")
print("Results Page:",URL)


# Statistics
num_bins = 20

fig, ax = plt.subplots()

props = dict(boxstyle='square', facecolor='orange', alpha=0.33)
ax.hist(filtered_prices, "auto", density=False, rwidth=0.9)
ax.text(0, 1.2, output_max_price+"\n"+output_min_price+"\n"+output_average, transform=ax.transAxes, fontsize=11, fontfamily="monospace", verticalalignment='top', bbox=props)
ax.set_xlabel('CHF') 
ax.set_ylabel('Sold Items') 

plt.subplots_adjust(bottom=0.1, left=0.1, right=0.98, top=0.8)
plt.show()