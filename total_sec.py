import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import ast

class windows_mvs:
    def __init__(self) -> None:
        self.today_date=datetime.today().strftime('%B %d, %Y')
        with open('last_scan_date.txt', 'r') as file:
            self.previous_modified_date=file.readlines()
        print(self.previous_modified_date[0])
        date_object = datetime.strptime(self.today_date, '%B %d, %Y')
        formatted_today_date =  date_object.strftime('%Y-%m-%d')
        with open('last_scan_date.txt', 'w') as file:
            file.writelines(formatted_today_date)
        date_object = datetime.strptime(self.previous_modified_date[0], '%Y-%m-%d')
        formatted_last_date =  date_object.strftime('%d %B, %Y')
        print("Last Scan Ran on -> ",formatted_last_date)


    def firefox(self):
        date='January 17, 2023'
        advisory_link_beteween_privious_and_today_date=[]
        firefox_response=requests.get('https://www.mozilla.org/en-US/security/advisories/')
        #print(firefox_response.text)
        ###################################################################################
        soup = BeautifulSoup(firefox_response.content, 'html.parser')
        cutoff_date = datetime.strptime(self.previous_modified_date[0], r'%Y-%m-%d')
        print(cutoff_date)
        for element in soup.find_all(['h2', 'ul']):
            if element.name == 'h2':
                date_str = element.text.strip()
                try:
                    #print(self.today_date)
                    
                    current_date = datetime.strptime(date_str, '%B %d, %Y')
                    #print(current_date)
                except ValueError:
                    continue
                
                if current_date > cutoff_date:
                    next_sibling = element.find_next_sibling('ul')
                    if next_sibling:
                        for link in next_sibling.find_all('a', href=True):
                            advisory_link_beteween_privious_and_today_date.append(link['href'])
          
        #print(advisory_link_beteween_privious_and_today_date)
        with open('windows.mvs','r') as mozilla:
            lines = mozilla.readlines()
            mozilla_line = ''
            for line in lines:
                if line.startswith('mozilla'):
                    mozilla_line = line.strip()
                    break

            mozilla_dict = ast.literal_eval(mozilla_line.split('=', 1)[1].strip())
        fixed_variable='https://www.mozilla.org'
        for each_link in advisory_link_beteween_privious_and_today_date:
            final_link=fixed_variable+each_link
            content=requests.get(final_link)
            a=content.text
            
            
            soup=BeautifulSoup(a,'html.parser')
            title_text=(soup.find('title'))
            title_text=str(title_text)
            title_text=title_text.replace('<title>','')
            title_text=title_text.replace('</title>','')
            title_text=title_text.replace(' — Mozilla','')
            title_text=title_text.replace('Security Vulnerability fixed in ','')

            title_text=title_text.split(',')

            title_text = [title.lower() for title in title_text if ('android' not in title.lower() and 'ios' not in title.lower() and 'pkcs#1 v1.5' not in title.lower() and ('esr' in title.lower() or 'thunderbird' in title.lower() or 'firefox' in title.lower()))]
            
            if len(title_text)<1:
                continue
            #print(title_text,'  ',final_link)
            cve_sections = soup.find_all('section', class_='cve')
            full_cve_id=[]
            for section in cve_sections:
                h4_tags = section.find('h4')
                full_cve_id.append(h4_tags.get('id'))
            #print(full_cve_id)
            
            product_info={}
            
            
            for i in title_text:
                if 'esr' in i:
                    version=re.findall('\d.+',title_text[0])
                    for k in range(len(version)):
                        octets = version[k].split('.')
                        while len(octets) < 4:
                            octets.append('0')
                        version[k] = '.'.join(octets[:4])
                    product_info.update({version[0]: full_cve_id})
                    
                    mozilla_dict['esr'][version[0]] = full_cve_id
                    
                if 'thunderbird' in i:
                    version=re.findall('\d.+',title_text[0])
                    for k in range(len(version)):
                        octets = version[k].split('.')
                        while len(octets) < 4:
                            octets.append('0')
                        version[k] = '.'.join(octets[:4])
                    product_info.update({version[0]: full_cve_id})
                    mozilla_dict['thunderbird'][version[0]] = full_cve_id
                    
                    
                if 'thunderbird' not in i and 'esr' not in i:
                    version=re.findall('\d.+',title_text[0])
                    for k in range(len(version)):
                        octets = version[k].split('.')
                        while len(octets) < 4:
                            octets.append('0')
                        version[k] = '.'.join(octets[:4])
                    print(version,'  ',final_link)
                    product_info.update({version[0]: full_cve_id})
                    print(product_info)
                    mozilla_dict['firefox'][version[0]] = full_cve_id
                    
        print(mozilla_dict)
        for i, line in enumerate(lines):
            if line.startswith('mozilla='):
                mozilla_line = line.strip()
                mozilla_dict_str = f"mozilla={mozilla_dict}\n"
                lines[i] = mozilla_dict_str
                break
        with open('windows.mvs', 'w') as file:
            file.writelines(lines)
        
            
    

windows_mvs_object=windows_mvs()
windows_mvs_object.firefox()