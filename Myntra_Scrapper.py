##################################### Imports
from selenium import webdriver
import urllib.request
import os
import json
import time
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
from bs4 import BeautifulSoup, SoupStrainer
import re
import pandas as pd

##################################### Image Downlaoding and path of Image
def img_downloader(img_url, img_name, save_fol):
    img_url = str(img_url)
    filename = str(img_name)
    r = requests.get(img_url, allow_redirects=True)
    #Stores Image location
    location = str(save_fol + filename)
    open(save_fol + filename, 'wb').write(r.content)
    return str(location)


###################################### get_json storing of all attributes
def get_json(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

    s = requests.Session()
    #Opening link in Bs4
    res = s.get(link, headers=headers, verify=False)

    soup = BeautifulSoup(res.text, "lxml")

    #looping all Script tags in HTML file
    script = None
    for s in soup.find_all("script"):
        s = str(s)
        #finding pdpdata for all attributes
        if 'pdpData' in s:
            start = s.index('{')
            script = s[22:-9]
            #print(script)
            break
    #returning a json load of pdpData
    return (json.loads(script))


################################### Selenium Opening Pages

driver = webdriver.Chrome('D:\Codes\Work\scrapping\chromedriver.exe')

#clicking to men page on myntra using selenium
driver.get('https://www.myntra.com/women')
time.sleep(5)
links = []

"""while True:
    time.sleep(5)
    for base in driver.find_element_by_class_name('myx-indexContainer'):
        links.append(base.find_element_by_xpath('./a').get_attribute("href"))
print(links)"""

i = 1

#Loops through all the pages on men page
while i < 10:
    driver.find_element_by_class_name(
        'desktop-searchBar').send_keys('women?p=2&plaEnabled=false'.format(i))
    driver.find_element_by_class_name('desktop-submit').click()

    #Save all Links on the pages
    for product_base in driver.find_elements_by_class_name('product-base'):
        links.append(product_base.find_element_by_xpath(
            './a').get_attribute("href"))
        """
        try:
            driver.find_element_by_class_name('pagination-next').click()
        except:
            driver.close()
            driver.quit()
        """
    i += 1

#################################### Extracting Data from json Object
fin_arr = []
for link_name in links:
    try:
        new = str(get_json(link_name))
        #print(new)
        #Slicing string
        new = new.replace('None', '0')
        p = re.compile('(?<!\\\\)\'')
        new = p.sub('\"', new)

        #print(new)

        '''
        Attributes used for scraping
        1.pdpData which contains id, name, etc.
        2.analytics containing Fabric,Hood,Length
        3.articleAttributes which has similar attributes
        4. Images has links which is helpful for downlaoding images later on.
        '''

        atr_arr = []
        attributes = ['"pdpData"','"analytics"','"articleAttributes"','"images"']

        #Looping through all attributes
        for j in attributes:
            article = '"'
            attr = new.index(j)
            i = 1
            cnt = 0
            #Creating dictionary of all the attributes
            while i > 0:
                if new[attr+i] != '{' and cnt == 0:
                    i+=1
                    continue
                cnt+=1
                if cnt>0:
                    article+=new[attr+i]
                    if new[attr+ i] == '}':
                        break
                i+=1
            if j == '"pdpData"':
                atr_arr.append(article[1:]+'}')
            else:
                atr_arr.append(article[1:])
        attr_dict = {}
        for i in atr_arr:
            json_ob = json.loads(i)
            for j in json_ob:
                attr_dict[j] = str(json_ob[j])

        #After a some string manupulation we get a combined dictionary of all the attributes.

        #Downlaoding Images
        image_path = img_downloader(str(attr_dict['imageURL']), str(attr_dict['id']) + '.jpg','D:/Codes/Work/scrapping/Myntra_women_images/')
        attr_dict.popitem()
        attr_dict.popitem()
        attr_dict.popitem()
        attr_dict.popitem()
        attr_dict.popitem()
        attr_dict['path'] = image_path #saving image path in dictionary.
        fin_arr.append(attr_dict)
    except :
        continue

######################################## Storing Data to CSV
df = pd.DataFrame(fin_arr)
col_name = 'path'
first_col = df.pop(col_name)
#Make path first coloum
df.insert(0, col_name, first_col)
df.to_csv('D:\Codes\Work\scrapping\scrape_female.csv')
