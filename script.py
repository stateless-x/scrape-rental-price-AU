from bs4 import BeautifulSoup
from csv import writer
import os
import re
import requests
from datetime import datetime

import interested_area

if not os.path.exists('output'):
    os.makedirs('output')

current_time = datetime.today().strftime('-%Y-%m-%d--%H-%M-%S')
area = interested_area.ADELAIDE
ourput_dir = 'output'
output_file = ourput_dir+'/sample.csv'
prop_type = 'apartment_units'
URL = f"https://www.rent.com.au/{prop_type}/{area}/"

# write headersg
with open (output_file,'w',encoding='utf-8', newline='') as f:
    w = writer(f)
    header = ['price', 'property_type', 'address', 'bed', 'bath', 'parking', 'link']
    w.writerow(header)

for page in range (1,100):
    try:
        res = requests.get(URL + 'p' + str(page) + '/')
        if res.status_code == 200:
            soup = BeautifulSoup(res.content,'html.parser')
            print(f"processing data at page: {page}...")
            # append data
            with open (output_file,'a',encoding='utf-8', newline='') as f:
                w = writer(f)
                lists = soup.find_all('article', class_='property-cell -normal')
                if not lists:
                    print(f"Done !")
                    raise SystemExit(0)

                for item in lists:
                    price = item.find('span', class_='price').text.strip('\n').split('\n', 1)[0].replace('to','-') #remove property type from price
                    price = re.sub('[^0-9\.]','', price).split('-') # remove all string from price tag
                    property_type = item.find('span',class_='property-type').text if item.find('span',class_='property-type') else None
                    address = item.find('h2', class_='address').text if item.find('h2', class_='address') else None
                    # extract url
                    for a in item.find_all('a',class_='asset'): 
                        link = a['href']
                    for ft in item.find_all('ul',class_='features'):
                        bed, bath, parking,*args = ft.find_all('span', class_='value')
                        bed = re.sub('[^0-9]','',bed.text) if bed else None
                        bath = re.sub('[^0-9]','',bath.text) if bath else None
                        parking= re.sub('[^0-9]','', parking.text) if parking else None
                    price = None if price[-1] == '' or (int(float(price[-1])) >= 4000) else int(float(price[-1])) 
                    info = [price, property_type, address, bed, bath, parking, link]
                    w.writerow(info)
        else:
            print(f"Error with status:{res.status_code}\nFile purged..")
            os.remove(output_file)
            raise SystemExit(0)     
    except Exception as e:
        print(e)
print("DONE..")
