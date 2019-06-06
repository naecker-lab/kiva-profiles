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

def access_source_code(url):
	url = f"https://www.kiva.org/lend/{url}"
	response = request.urlopen(url)
	soup = BeautifulSoup(response, 'lxml')
	try:
		soup = BeautifulSoup((str(soup).replace('<br/>','\n')), 'lxml') #removes line breaks in BS element so everything fits in image 
	except:
		soup = soup
	soup.prettify('utf-8')
	return soup 


## Function removes extra line-breaks, header and footer of page 
def clean_up(page):
	
	try:
		page.find('div', {'class': 'full-width-green-bar'}).decompose()
	except:
		pass

	try:
		for x in page.findAll("div","xbLegacyNav"):
			x.decompose()
	except:
		pass
	
	#remove the 'More information about this loan' part 
	
	try:
		page.find('section', {'class': 'more-loan-info'}).decompose()
		page.find('section', {'class': 'more-loan-info'}).find_previous_sibling('hr').decompose()
	except:
		pass

	#Remove the 'A loan of xxx helped a member...' part 
	try:
		page.find('div', {'class':'loan-use'}).decompose()
		page.find('div', {'class': 'loan-use'}).find_previous_sibling('hr').decompose()
	except:
		pass

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
	
	try:
		page.find('p', {'class': 'borrowers-list'}).decompose()
	except:
		pass
	'''
	#add image back to html
	try:
		#borrower_image = page.find('div', {'class': 'row loan-image-info-row'})
		borrower_image = page.findAll('img')
	except:
		pass 
	return borrower_image
	'''
	#removes all line breaks
	try:
		page.findAll('hr').decompose()
	except:
		pass

	#genarate thumbnails 
	return page

def cleanUp_for_thumbnail(page):
	try:
		page = page.find('div', attrs={'class': 'borrower-profile-pieces'}).clear()
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
	try:
		page.find('div', attrs={'class': 'right-content columns'}).clear()
	except:
		pass
	
	try:
		page.find('section', attrs={'class': 'loan-details'}).clear()
	except:
		pass
	
	try:
		for e in page.findAll("div","stat"):
			e.clear()
	except:
		pass
	return

def extend_text(page):
	div_page_content = page.find("div", { "class" : "borrower-profile-pieces" })
	button_active = page.new_tag('style', type='text/css')
	div_page_content.attrs['style'] = 'background: #FFF'
	
	div_page_content = page.find("div", { "class" : "right-content columns" })
	button_active = page.new_tag('style', type='text/css')
	try:
		div_page_content.attrs['style'] = 'background-color: white'
	except:
		pass
	try:
		search = page.find("div", { "class" : "left-content columns" })
		search['class'] = 'columns'
	except:
		pass

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
        page.find('section', attrs={'class': 'country-info'}).clear()
    except:
        pass
    
    return


def generate_output(loanID,page, bGenerateImage):
	s = str(loanID)
	html_file = '%s.html' % str(loanID)  
	current_dir = os.getcwd()
	working_dir = os.path.join(current_dir,html_file)
	#os.mkdir('thumbnails') 
	#thumbnail_dir = os.path.join(current_dir,r'thumbnails')
	
	with open(working_dir, "w+") as file:
		file.write(str(page))

	if bGenerateImage: ## Use pdfcrowd API to convert html to png output 
		client = pdfcrowd.HtmlToImageClient('danbjork', 'b36c2753c910a1b758fbf6409ed06310')
		client.setUseHttp(True)
		client.setOutputFormat('png')
		client = client.setScreenshotHeight(1250)
		client.convertFileToFile(working_dir, '%s.png' % str(loanID))

def generate_thumbnail(loanID, page):
	s = str(loanID)
	html_file = '%s.html' % str(loanID)  
	current_dir = os.getcwd()
	working_dir = os.path.join(current_dir,html_file)

	if os.path.exists('./thumbnails') == False:
		os.makedirs('thumbnails')
		thumbnail_dir = os.path.join(f'{current_dir}/thumbnails', html_file)
		with open(thumbnail_dir, 'w+') as thumbnail_file:
			thumbnail_file.write(str(page))
			
		'''
		client = pdfcrowd.HtmlToImageClient('danbjork', 'b36c2753c910a1b758fbf6409ed06310')
		client.setUseHttp(True)
		client.setOutputFormat('png')
		client = client.setScreenshotHeight(1250)
		client.convertFileToFile(thumbnail_dir, '%s.png' % str(loanID))
		'''
	else:
		thumbnail_dir = os.path.join(f'{current_dir}/thumbnails', html_file)
		with open(thumbnail_dir, 'w+') as thumbnail_file:
			thumbnail_file.write(str(page))

		## Use pdfcrowd API to convert html to png output 
		'''
		client = pdfcrowd.HtmlToImageClient('danbjork', 'b36c2753c910a1b758fbf6409ed06310')
		client.setUseHttp(True)
		client.setOutputFormat('png')
		client = client.setScreenshotHeight(1250)
		client.convertFileToFile(thumbnail_dir, '%s.png' % str(loanID))
		'''

def extract_loanID_from_URL(x ):
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
	cleaned_page = clean_up(webpage)
	capture_top_right(cleaned_page)
	capture_bottom_right(cleaned_page)
	extend_text(cleaned_page)
	capture_bottom_left(cleaned_page)
	generate_output(nLoanID, cleaned_page, False)

for nLoanID in anLoanIDs:
	webpage = access_source_code(nLoanID)
	cleaned_page = clean_up(webpage)
	capture_top_right(cleaned_page)
	capture_bottom_right(cleaned_page)
	extend_text(cleaned_page)
	capture_bottom_left(cleaned_page)
	cleanUp_for_thumbnail(cleaned_page)
	generate_thumbnail(nLoanID,cleaned_page)