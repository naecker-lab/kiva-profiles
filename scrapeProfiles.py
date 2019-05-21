import requests
import bs4
import pdfcrowd
import subprocess
import sys
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import re

bJeff          = True
bGenerateImage = False

## Get the html code of webpage and convert into 'Beautiful Soup' element for parsing
def access_source_code(url):
	if bJeff:
		chrome_driver_binary = "/Users/jnaecker/Downloads/chromedriver"
	else:
		chrome_driver_binary = "/Users/danbjork/Downloads/chromedriver"
	
	options = webdriver.ChromeOptions()
	if bJeff:
		options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
	else:
		options.binary_location = "/Applications/Chrome.app/Contents/MacOS/Google Chrome"
	
	browser = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
	webpage = "https://www.kiva.org/lend/" + str(url)
	browser.get(webpage)
	html = browser.page_source
	soup = BeautifulSoup(html,"lxml")
	return soup 

## Function removes extra line-breaks, header and footer of page 
def clean_up(page):
	question_action = page.find('div', attrs={'class': 'full-width-green-bar'})
	question_action.clear()
	
	for x in page.findAll("div","xbLegacyNav"):
		x.decompose()
	
	line = page.find('section', {'class': 'more-loan-info'})
	if page.find('section', {'class': 'more-loan-info'}) is not None: 
	    line = page.find('section', {'class': 'more-loan-info'}).find_previous_sibling('hr')
	    if line is not None:
	        line.decompose()
	
	line2 = page.find('section', {'class': 'lenders-teams'})
	if page.find('section', {'class': 'lenders-teams'}) is not None: 
	    line2 = page.find('section', {'class': 'lenders-teams'}).find_previous_sibling('hr')
	    if line2 is not None:
	        line2.decompose()
	    
	line3 = page.find('section', {'class': 'country-info'})
	if page.find('section', {'class': 'country-info'}) is not None: 
	    line3 = page.find('section', {'class': 'country-info'}).find_previous_sibling('hr')
	    if line3 is not None:
	        line3.decompose()
	
	line4 = page.find('section', {'class': 'loan-tags'})
	if page.find('section', {'class': 'loan-tags'}) is not None: 
	    line4 = page.find('section', {'class': 'loan-tags'}).find_previous_sibling('hr')
	    if line4 is not None:
	        line4.decompose()


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
	
	x = page.find('div', {'aria-controls': 'ac-more-loan-info-body'})
	if x is not None:
		temp = x.find('h2')
		if temp is not None:
			temp.clear()
	
	tags_text = page.find('div', {'class': 'ac-title-text'})
	if tags_text is not None:
	    tags_text.clear()
	
	lenders = page.find('section', attrs={'class': 'lenders-teams'})
	lenders.clear()
	
	country_info = page.find('section', attrs={'class': 'country-info'})
	country_info.clear()
	
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
	return


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
	generate_output(nLoanID, webpage, bGenerateImage)

