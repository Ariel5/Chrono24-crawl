import re
import time
import random
import requests
import unidecode
import pandas as pd
from bs4 import BeautifulSoup as bs



headers = {'accept': '*/*',
 'accept-encoding': 'gzip, deflate',
 'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
 'cookie': 'uid=9c718efe-dcca-4e71-b92d-c3dd7b7f06cc',
 'referer': 'https://a3853408329f84107a5d2b90c11d7c4b.safeframe.googlesyndication.com/',
 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
 'sec-ch-ua-mobile': '?0',
 'sec-ch-ua-platform': '"Windows"',
 'sec-fetch-dest': 'empty',
 'sec-fetch-mode': 'cors',
 'sec-fetch-site': 'same-origin',
 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}


def get_links_from_single_page(url):
    # This gets the Pagination of the page e.g. page 1 of 10, 2 of 10 ...
    links = []
    
    #to add reference to variable brand. Rolex link is placeholder
    #url = f'https://www.chrono24.com/{brand}/index.htm'

    r = requests.get(url, headers=headers)

    soup = bs(r.text, 'html.parser')

    data = soup.findAll('div', {"class":"article-item-container wt-search-result"})

    for div in data:
        link = div.findAll('a')
        for a in link:
            links.append("https://www.chrono24.com" + a['href'])

    links.remove('https://www.chrono24.com/about-us.htm')
    
    return links


def get_brand_list():
    url = 'https://www.chrono24.com/search/browse.htm?char=A-Z'  
    
    r = requests.get(url, headers=headers)

    ChronoBS = bs(r.text, 'html.parser')

    get_brands = ChronoBS.find_all("div", {"class":"brand-list"})[-1].get_text()

    brands = []

    def Convert(string):
        normalized_string = unidecode.unidecode(string)
        brands = list(normalized_string.split("\n"))
        new_list=[x for x in brands if len(x)>=2]
        return new_list

    r = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in Convert(get_brands)]

    brands_df = pd.DataFrame(r, columns = ['Brand'])
    brands_df.drop(brands_df.tail(1).index,inplace=True)
    brands_df = brands_df.applymap(lambda s: s.lower() if type(s) == str else s)
    brands_df.to_csv('brands_list.csv', sep = ',', index = False)
    return brands_df


def get_max_pages(brand):
    
    #to add reference to variable brand. Rolex link is placeholder
    url = f'https://www.chrono24.com/{brand}/index.htm'

    r = requests.get(url, headers=headers)

    soup = bs(r.text, 'html.parser')

    # This gets the Pagination of the page e.g. page 1 of 10, 2 of 10 ...
    data = soup.findAll('ul', {"class":"pagination list-unstyled pull-xs-none pull-sm-right"})
    
    li = []
    for ultag in data:
        for litag in ultag.find_all('li'): # Process list elements
            normalized_li = litag.text.split("\n")
            new_list=[x for x in normalized_li if len(x)>=1]
            li.append(new_list)
    
    # Create flat list
    flat_li = [item for sublist in li for item in sublist]
    flat_li = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in flat_li]

    # index = 1

    # TODO Ariel Why?
    if len(flat_li) > 1:
        index = int(flat_li[-2])
    else:
        index = 1

    return index



#Get ad info... brand, model, reference, etc.

def fetch_attributes(url):
    # TODO what is this?

    # URL with actual price listings for the GMT Batman
    #url = 'https://www.chrono24.com/rolex/rolex-gmt-master-ii-2020-batman--batgirl-ref-126710blnr-ceramic-jubilee-stainless-steel--id20749471.htm'

    r = requests.get(url, headers=headers)

    soup = bs(r.text, 'html.parser')
    
    # TODO Remove this BS. Just download the watch page
    # 1. Find this <div article-item-container wt-search-result>
    # 2. Open the link
    # 3. Download the page
    # 4. Done
    if soup.findAll('span', {"class":'js-price-shipping-country'}):
        price = {'Price' : soup.findAll('span', {"class":'js-price-shipping-country'})[0].get_text()}
    else:
        price = {'Price' : soup.findAll('span', {"class":'price-md'})[0].get_text()}
       
    data = soup.findAll('div', {"class":"col-xs-24 col-md-12 m-b-6 m-b-md-0"})
    
    li = []
    for tag in data:
            for trtag in tag.find_all('tr'):
                normalized_tr = trtag.text.split("\n")
                new_list=[x for x in normalized_tr if len(x)>=2]
                li.append(new_list)
    attributes_dict = {x[0]: x[1:] for x in li}
    new_dict = {k: str(v).replace('[','').replace(']', '') for k,v in attributes_dict.items()}
    new_dict = {k: str(v).replace("'",'').strip() for k,v in new_dict.items()}
    new_dict = {k: str(v).replace('"','').strip() for k,v in new_dict.items()}
    clean_attributes = {k: v for k, v in new_dict.items() if v != ''}
    clean_attributes.update(price)

    return clean_attributes



import random

def get_all_links(brand):
    # This gets all pagination links for a brand

    all_links = []
    # for brand in brands_list['Brand']: # Doing this for all brands is too much
        
    # TODO This might get you banned!
    time.sleep(random.uniform(1.5,3))
    
    for index in range(1, get_max_pages(brand)+1):
        
        if index == 1:
            all_links.append(f'https://www.chrono24.com/{brand}/index.htm')
            print (f'https://www.chrono24.com/{brand}/index.htm')
        else:
            all_links.append(f'https://www.chrono24.com/{brand}/index-{index}.htm')
            print (f'https://www.chrono24.com/{brand}/index-{index}.htm')
#         time.sleep(0.25)
        


    links_df = pd.DataFrame(all_links, columns = ['Brand'])
    links_df.drop(links_df.tail(1).index,inplace=True)
    links_df = links_df.applymap(lambda s: s.lower() if type(s) == str else s)
    links_df.to_csv('link_list.csv', sep = ',', index = False)

    #return all_links  


def get_all_ads():
    # This processes all paginations for all brands in link_list

    ad_links = []
    
    for index, link in enumerate(link_list['Brand']):
            ad = (get_links_from_single_page(link))
            ad_links.append(ad)
            
            if index % 50 == 0:
                print(str(ad))
            
    flat_li = [item for sublist in ad_links for item in sublist]
    flat_li.remove('https://www.chrono24.com/about-us.htm')
    
    ad_df = pd.DataFrame(flat_li, columns = ['Brand'])
    ad_df.drop(ad_df.tail(1).index,inplace=True)
    ad_df.to_csv('ad_list.csv', sep = ',', index = False)
    
    
#     return flat_li