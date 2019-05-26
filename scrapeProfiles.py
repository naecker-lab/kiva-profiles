import requests
import lxml 
import bs4
import pdfcrowd
import subprocess
from urllib import request

import sys
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import re

## Make HTTP request for the url, convert response into 'BeautifulSoup' object for parsing
def access_source_code(url):
    url = f"https://www.kiva.org/lend/{url}"
    response = request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    soup.prettify('utf-8')
    return soup 


## Function removes extra line-breaks, header and footer of page 
def clean_up(page):
    page.find('div', {'class': 'full-width-green-bar'}).decompose()
    for x in page.findAll("div","xbLegacyNav"):
        x.decompose()

    #remove the 'More information about this loan' part 
    try:
        page.find('section', {'class': 'more-loan-info'}).decompose()
        page.find('section', {'class': 'more-loan-info'}).find_previous_sibling('hr').decompose()
    except:
        pass

   
    #Remove the 'A loan of xxx helped a member...' part 
    #page.find('meta', {'property':'og:description'}).decompose()
    #page.find(content=re.compile(r'^A loan of')).decompose()
    
    #Removes the 'Lenders and lending teams' part
    try:
        page.find('section', {'class': 'lenders-teams'}).decompose()
        page.find('section', {'class': 'lenders-teams'}).find_previous_sibling('hr').decompose()
    except:
        pass
  
    #Removes country information 
    try:
        page.find('section', {'class': 'country-info'}).decompose()
        page.find('section', {'class': 'country-info'}).find_previous_sibling('hr').decompose()
    except:
        pass
    
    #Removes loan tags 
    try:
        page.find('section', {'class': 'loan-tags'}).decompose()
        page.find('section', {'class': 'loan-tags'}).find_previous_sibling('hr').decompose()
    except:
        pass

    #Removes the photo and text line about translation
    try:
        page.find('section', {'class': 'loan-translation ac-container'}).decompose()
    except:
        pass

    return page


def capture_top_right(page):
	lender_count = page.find('a', attrs={'class': 'lender-count black-underlined'})
	lender_count.clear()
	
	status = page.find('div', attrs={'class': 'current-status-meter'})
	status.clear()
	
	lender_action = page.find('div', attrs={'class': 'show-for-large-up lend-action'})
	lender_action.clear()
	
	return

def capture_bottom_right(page):
	right_info = page.find('div', attrs={'class': 'right-content columns'})
	right_info.clear()
	
	details = page.find('section', attrs={'class': 'loan-details'})
	details.clear()
	
	for e in page.findAll("div","stat"):
		e.clear()
	
	return

def extend_text(page):
	div_page_content = page.find("div", { "class" : "borrower-profile-pieces" })
	button_active = page.new_tag('style', type='text/css')
	div_page_content.attrs['style'] = 'background: #FFF'
	
	div_page_content = page.find("div", { "class" : "right-content columns" })
	button_active = page.new_tag('style', type='text/css')
	div_page_content.attrs['style'] = 'background-color: white'
	
	search = page.find("div", { "class" : "left-content columns" })
	search['class'] = 'columns'

def capture_bottom_left(page):
    try:
        page.find('div', {'aria-controls': 'ac-more-loan-info-body'}).find('h2').clear()
    except:
        pass 
    
    try:
        page.find('div', {'class': 'ac-title-text'}).clear()
    except:
        pass
    
    try:
        page.find('section', attrs={'class': 'lenders-teams'}).clear()
    except:
        pass
    
    try:
        country_info = page.find('section', attrs={'class': 'country-info'}).clear()
    except:
        pass
    
    return

def generate_output(url,page, bGenerateImage):
	s = str(url)
	fl = '%s.html' % str(url)  
	di = os.getcwd()
	final = os.path.join(di,fl)  
	
	with open(final, "w") as file:
		file.write(str(page))

	if bGenerateImage: ## Use pdfcrowd API to convert html to png output 
		client = pdfcrowd.HtmlToImageClient('danbjork', 'b36c2753c910a1b758fbf6409ed06310')
		client.setUseHttp(True)
		client.setOutputFormat('png')
		client = client.setScreenshotHeight(1250)
		client.convertFileToFile(final, '%s.png' % str(url))

def extract_loanID_from_URL( x ):
	m = re.search('^http(s)?://www.kiva.org/lend/(\\d+$)', x)
	return m.group(2)

try:
	## Read file with URLs, one per line
	url_file = sys.argv[1]
	file = open(url_file, 'r')
	url_list = [ x.strip("\r\n") for x in file if x != '' ]
	anLoanIDs = [ extract_loanID_from_URL(x) for x in url_list ]
	file.close()
except IndexError:
	## Ask for user-input in the form of space-separated url numbers
	anLoanIDs = [extract_loanID_from_URL(x) for x in input("Enter space-separated urls: ").split()]

## Run and generate output for each entered user 'url'
for nLoanID in anLoanIDs:
	webpage = access_source_code(nLoanID)
	clean_up(webpage)
	capture_top_right(webpage)
	capture_bottom_right(webpage)
	extend_text(webpage)
	capture_bottom_left(webpage)
	generate_output(nLoanID, webpage, True)