"""
This is the scraper for box office mojo.
As of 9/29/2023

We get the title, the revenues, and summary data based on the home page for a movie
on Box Office Mojo

"""

from bs4 import BeautifulSoup
import requests
import html5lib
import numpy as np
import re

#This gets the title
def get_title(sp):
    title = sp.find("h1", attrs={"class":"a-size-extra-large"}).getText()
    return title

#This gets the revenues
def get_rev(sp):
    #dictionary to return called rev
    rev = {}
    #find the table where revenue is
    table = sp.find("div", attrs={"class": "a-section a-spacing-none mojo-performance-summary-table"})
    #store revenues as we search
    revenues = []
    #find spans that contain revenue
    for row in table.findAll("span", attrs={"class" : "a-size-medium a-text-bold"}):
        #get the money and clean the text
        money = row.findAll("span", attrs={"class":"money"})
        for m in money:
            dol = m.get_text().split("$")
            dol = "".join(dol[1].split(","))
            #return the int
            revenues.append(int(dol))
    #Get the types of revenue displayed
    type_of_rev = []
    #search for revenues
    for t in table.findAll("span", attrs={"class":"a-size-small"}):
        for line in list(set(t.get_text().split(" "))):
            if line.isalpha() : type_of_rev.append(line)
    #make dictionary of type of revenue: revenue
    for i in range(len(revenues)):
        rev[type_of_rev[i]] = revenues[i]
    #return 
    return rev

#gets all data available in the page
def get_summary_data(sp):
    # find where the summary statistics are
    table = sp.find("div", attrs={"class": "a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile"})
    #see what data is available
    avail_data = []
    # search for the type of data
    for row in table.findAll("div", attrs={"class":"a-section a-spacing-none"}):
        # We do not want imdb pro promotion
        if "IMDbPro" not in row.find("span").get_text() : avail_data.append(row.find("span").get_text())
    #get tge table again
    table = sp.find("div", attrs={"class": "a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile"})
    #we store the actual data here
    data = []
    #decide whether or not to store the next line, this is because there are duplicates
    store_next = False
    #search for data
    for t in table.findAll("span"):
        if store_next == True:
            data.append(t.getText().strip())
            store_next = False
        if t.getText().strip() in avail_data:
            store_next = True
    #we want to format some of the data differently
    formatted_data = []
    for d in data:
        a = " ".join(d.split("\n"))
        a = " ".join(a.split(" "))
        a = re.sub(' +', ' ', a)
        a = a.strip()
        if "See full" in a:
            a = a.split("See full")[0]
            formatted_data.append(a.strip())
        elif "$" in a:
            dol = a.split("$")
            dol = "".join(dol[1].split(","))
            formatted_data.append(int(dol))
        else:
            formatted_data.append(a.strip())
    #store in dictionary
    data_dict = {}
    for i in range(len(avail_data)):
        data_dict[avail_data[i]] = formatted_data[i]

    return data_dict

# Get summary data, title, and revenues
def get_data_by_id(id):
    #read in the URL
    URL = f"https://www.boxofficemojo.com/title/{id}/?ref_=bo_se_r_2"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html5lib")
    #get the data
    title = get_title(soup)
    revenue = get_rev(soup)
    data = get_summary_data(soup)
    data["Title"] = title
    data["Revenue"] = revenue
    data["IMDB ID"] = id
    #return
    return data


def main():
    print("===== Running Scraper =====")
    return 

if __name__ == "__main__":
    main()

