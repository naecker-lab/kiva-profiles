import requests
import lxml 
import bs4
import pdfcrowd
import subprocess
from urllib import request
import sys
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re
import time
from PIL import Image
from io import BytesIO

#locations of executables of webdrivers
chromedriver_location = r"G:\dev\chromedriver\chromedriver"
geckodriver_location = r'G:\dev\geckodriver\geckodriver.exe'
chromedriver_location = r"drivers/chromedriver"
geckodriver_location = r"drivers/geckodriver"


nDeltaPx = 70

def get_thumbnail(loanID):
    print(f'Capturing loan {loanID}')
    options = FirefoxOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Firefox(options=options, executable_path=geckodriver_location)
    driver.get(f'https://www.kiva.org/lend?queryString={loanID}&status=all')
    time.sleep(5)
    
    #close the cookies notification:
    driver.find_element_by_class_name('close-button').click()
    
    #remove green bar header
    try:
        element2 = driver.find_element_by_class_name('full-width-green-bar')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element2)
    except:
        pass 
    
    #also removes header
    try:
        element3 = driver.find_element_by_class_name('xbLegacyNav')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element3)
    except:
        pass 
    
    #remove footer
    try:
        element9 = driver.find_element_by_xpath('//*[@id="lend"]/div[5]')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element9)
    except:
        pass 
    
    try:
        element15 = driver.find_element_by_class_name('carousel-nav')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element15)
    except:
        pass
    
    
    try:
        el = driver.find_element_by_class_name('heading-region')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, el)
    except:
        pass
    
    try:
        el = driver.find_element_by_class_name('control-region')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, el)
    except:
        pass
    
    try:
        el = driver.find_element_by_class_name('fundraising-meter')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, el)
    except:
        pass
    
    try:
        el = driver.find_element_by_class_name('left-and-to-go-line')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, el)
    except:
        pass
    
    # REMOVE MATCHING INDICATOR IF IT ALREADY EXISTS
    try:
        elementMatched = driver.find_element_by_class_name('matching-line')
        driver.execute_script("""
        var element = arguments[0];
        element.innerHTML = '';
        """, elementMatched)
    except:
        pass
    
    # CHANGE HEIGHT OF CARD
    # try:
    #     elementMatched = driver.find_element_by_class_name('loan-card-2')
    #     driver.execute_script("""
    #     var element = arguments[0];
    #     element.style = 'height: 400px;';
    #     """, elementMatched)
    # except:
    #     pass
    
    for bMatched in (False, True):
        cExtra = 'ma' if bMatched else 'un'
        if bMatched:
            # ADD MATCHING INDICATOR
            element_imageFooter = driver.find_element_by_class_name('matching-line')
            driver.execute_script("""
            var element = arguments[0];
            element.innerHTML = '<svg class="icon icon-match"><use xlink:href="#icon-match"></use></svg><span>Matching by a Kiva supporter</span>';
            """, element_imageFooter)
        
        
        #convert page to BS element for further cleaning up
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        soup.prettify()
        
        if not os.path.exists(str(f'{str(os.getcwd())}/thumbnail_html')):
            os.makedirs('thumbnail_html')
        
        with open(f'{str(os.getcwd())}/thumbnail_html/{str(loanID)}{cExtra}.html', 'w+', encoding='utf-8') as page_source:
            page_source.write(str(soup))
        
        
        #generate thumbnails using headless part 
        options = FirefoxOptions()
        options.add_argument("--headless")
        
        driver_headless = webdriver.Firefox(options=options,executable_path=geckodriver_location)
        
        driver_headless.get(f'file:///{str(os.getcwd())}/thumbnail_html/{str(loanID)}{cExtra}.html')
        time.sleep(10)
        
        # body = driver_headless.find_element_by_css_selector('.loan-image-info-row')
        body = driver_headless.find_element_by_class_name('loan-card-2')
        body_size = body.size
        body_location = body.location
        
        body_screenshot = driver_headless.get_screenshot_as_png()
        
        left = body_location['x']
        top = body_location['y']
        
        right = left + body_size['width']
        bottom = top + body_size['height'] - nDeltaPx
        
        im = Image.open(BytesIO(body_screenshot))
        im = im.crop((left, top, right, bottom))
        
        if not os.path.exists(f'{str(os.getcwd())}/thumbnail_png'):
            os.makedirs('thumbnail_png')
        
        im.save(f'{str(os.getcwd())}/thumbnail_png/{str(loanID)}{cExtra}.png')
        driver_headless.quit()
    
    driver.quit()


def get_detail(loanID):
    print(f'Capturing loan {loanID}')
    options = FirefoxOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Firefox(options=options, executable_path=geckodriver_location)
    driver.get(f'https://www.kiva.org/lend/{loanID}?minimal=false')
    time.sleep(5)
    
    #close the cookies notification:
    driver.find_element_by_class_name('close-button').click()
    
    #remove lenders-teams
    try: 
        element1 = driver.find_element_by_class_name('lenders-teams')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element1)
    except:
        pass 
    
    #remove loan endorser
    try:
        element1b = driver.find_element_by_class_name('endorser')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element1b)
    except:
        pass 
    
    #remove loan endorser
    try:
        element1c = driver.find_element_by_class_name('comments-and-updates')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element1c)
    except:
        pass 
    
    #remove status meter
    try:
        element1d = driver.find_element_by_class_name('current-status-meter')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element1d)
    except:
        pass 
    
    #remove green bar header
    try:
        element2 = driver.find_element_by_class_name('full-width-green-bar')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element2)
    except:
        pass 
    
    #also removes header
    try:
        element3 = driver.find_element_by_class_name('xbLegacyNav')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element3)
    except:
        pass 
    
    try:
        element4 = driver.find_element_by_class_name('more-loan-info')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element4)
    except:
        pass 
    
    try:
        element5 = driver.find_element_by_xpath('//*[@id="main"]/div[6]/div[2]')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element5)
    except:
        pass 
    
    #remove footer
    try:
        element9 = driver.find_element_by_xpath('//*[@id="lend"]/div[5]')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element9)
    except:
        pass 
    
    #remove country-info 
    try:
        element10 = driver.find_element_by_xpath('//*[@id="country-section"]')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element10)
    except:
        pass
    
    #remove loan-tags 
    try:
        element11 = driver.find_element_by_class_name('loan-tags')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element11)
    except:
        pass
    
    #remove 'translated by ...'
    try:
        element12 = driver.find_element_by_xpath('//*[@id="ac-loan-story-body"]/section[2]')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element12)
    except:
        pass 
    
    try:
        element13 = driver.find_element_by_xpath('//*[@id="ac-loan-story-body"]/p')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element13)
    except:
        pass 
    
    #remove image carousel
    try:
        element14 = driver.find_element_by_class_name('carousel-nav')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element14)
    except:
        pass
    
    try:
        element15 = driver.find_element_by_class_name('carousel-nav')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element15)
    except:
        pass
    
    for i in range(8):
        try:
            el = driver.find_element_by_class_name('line-break')
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, el)
        except:
            pass
    
    # REMOVE MATCHING INDICATOR IF IT ALREADY EXISTS
    try:
        elementMatched = driver.find_element_by_class_name('matching-message')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, elementMatched)
    except:
        pass
    
    for bMatched in (False, True):
        cExtra = 'ma' if bMatched else 'un'
        if bMatched:
            # ADD MATCHING INDICATOR
            element_imageFooter = driver.find_element_by_class_name('loan-image-footer')
            driver.execute_script("""
            var matchingIndicator = document.createElement("div");
            matchingIndicator.className = "matching-message";
            matchingIndicator.innerHTML = '<svg class="icon icon-match"><use xlink:href="#icon-match"></use></svg><span aria-describedby="tooltip-k2djrzq50" aria-haspopup="true" data-selector="tooltip-k2djrzq50" data-tooltip="" title="">Matching by a Kiva supporter</span>';
            var element = arguments[0];
            element.appendChild(matchingIndicator);
            """, element_imageFooter)
        
        
        # <div class="loan-image-footer" style="position: relative; transition: margin 0.3s ease-in-out 0s; margin-right: -1px; margin-left: 0px; margin-top: 0px; display: block;">
        # cMatchingIndicator = '<div class="matching-message">\
                              # <svg class="icon icon-match"><use xlink:href="#icon-match"></use></svg>\
                              # <span aria-describedby="tooltip-k2djrzq50" aria-haspopup="true" data-selector="tooltip-k2djrzq50" data-tooltip="" title="">Matching by a Kiva supporter</span>\
                              # </div>'
        #</div>'
        
        #remove bottom right part for loan details 
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
        
        #convert page to BS element for further cleaning up
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        soup.prettify()
        capture_bottom_right(soup)
        extend_text(soup)
        
        try:
            (soup.find('section', {'class': 'loan-description'}).find('p')).replaceWith((soup.find('section', {'class': 'loan-description'}).find('p')).get_text())
        except:
            pass 
        
        
        #removes current status of loan part 
        try:
            soup.find('div', {'class': 'current-status-meter'}).clear()
        except:
            pass 
        
        #remove lend-action-holder
        try:
            soup.find('div', {'class': 'lend-action-holder'}).clear()
        except:
            pass 
        
        #removes the 'a loan of zzz...' part 
        try:
            soup.find('div', {'class': 'small-12 columns'}).clear()
        except:
            pass 
        
        try:
            soup.find('p', {'class': 'ac-title black-underlined text-center show-previous-loan-details'}).clear()
        except:
            pass 
        
        
        # <div class="loan-image-footer" style="position: relative; transition: margin 0.3s ease-in-out 0s; margin-right: 179px; margin-left: 180px; margin-top: 0px; display: block;">
                        # 
                    # </div>
        # soup.find('div', {'class': 'loan-image-footer'}).clear()
        # matchingIndicator = soup.new_tag("div", attrs={"class":"matching-message"})
        
        if not os.path.exists(str(f'{str(os.getcwd())}/detail_html')):
            os.makedirs('detail_html')

        with open(f'{str(os.getcwd())}/detail_html/{str(loanID)}{cExtra}.html', 'w+', encoding='utf-8') as page_source:
            page_source.write(str(soup))
        

        #generate thumbnails using headless part 
        options = FirefoxOptions()
        options.add_argument("--headless")
        
        driver_headless = webdriver.Firefox(options=options,executable_path=geckodriver_location)
        
        driver_headless.get(f'file:///{str(os.getcwd())}/detail_html/{str(loanID)}{cExtra}.html')
        time.sleep(10)
        
        #close the cookies notification:
        driver_headless.find_element_by_class_name('close-button').click()
        
        image = driver_headless.find_element_by_css_selector('.loan-image-info-row')
        image_size = image.size
        image_location = image.location

        body = driver_headless.find_element_by_class_name('borrower-profile-wrapper')
        body_size = body.size
        body_location = body.location
        
        screenshot = driver_headless.get_screenshot_as_png()
        
        # use image width to narrow focus
        # left = body_location['x']
        left = image_location['x']
        top  = body_location['y']
        
        # right = left + body_size['width']
        right = left + image_size['width']
        bottom = top + body_size['height']
        
        im = Image.open(BytesIO(screenshot))
        im = im.crop((left, top, right, bottom))
        
        if not os.path.exists(f'{str(os.getcwd())}/detail_png'):
            os.makedirs('detail_png')
        
        im.save(f'{str(os.getcwd())}/detail_png/{str(loanID)}{cExtra}.png')
        driver_headless.quit()
    
    driver.quit()



#read .txt file with URLs
def extract_loanID_from_URL(x ):
    m = re.search('^http(s)?://www.kiva.org/lend/(\\d+)(\\?minimal=false)?$', x)
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

#for each loanID, generate cleaned_html, full_image, thumbnail
for loanID in anLoanIDs:
    try:
        # get_thumbnail(loanID) 
        get_detail(loanID)
    except:
        pass

