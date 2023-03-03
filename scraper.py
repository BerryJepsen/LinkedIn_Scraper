from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

webdriver_path = r'./chromedriver_mac_arm64/chromedriver' #chromedriver path
username = r'' #tester's linkedin username
password = r''#tester's linkedin password
linkedin_links = [r'https://www.linkedin.com/in/mike-nolan-b82754a/'] #the linkedin profiles to be scraped
output_root = r'./result' #the linkedin profiles output root

chrome_options = Options()
#chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')


browser = webdriver.Chrome(executable_path = webdriver_path)
browser.get('https://www.linkedin.com/uas/login')

#logging in
browser.find_element_by_id('username').send_keys(username)
time.sleep(1)
browser.find_element_by_id('password').send_keys(password)
time.sleep(1)
browser.find_element_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[3]/button').click()
time.sleep(1)

#scrape function
def scrape(link, browser):
    '''

    :param link: linkedin link to scrape
    :param browser: webdriver
    :return: result dictionary
    '''
    assert isinstance(link, str)
    NAME = None
    TITLE = None
    LOCATION = None
    ABOUT = None
    EXPERIENCE = []
    EDUCATION = []
    RECOMMENDATION = []

    browser.get(link)
    time.sleep(1)
    soup = BeautifulSoup(browser.page_source, 'lxml')

    #getting name
    try:
        div = soup.find('div', {'class': 'pv-text-details__left-panel'})
        NAME = div.find('h1').get_text().strip()
    except:
        pass

    # getting title
    try:
        TITLE = div.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()
    except:
        pass

    # getting location
    try:
        LOCATION = soup.find('div', {'class': 'pv-text-details__left-panel mt2'}).find('span').get_text().strip()
    except:
        pass

    # getting about
    try:
        ABOUT = browser.find_element_by_id("about").find_element_by_xpath("..").find_element_by_class_name("display-flex").text
    except:
        pass

    # getting experience
    try:
        browser.get(os.path.join(link, "details/experience"))
        time.sleep(1)
        for exp in browser.find_elements_by_class_name('pvs-list__paged-list-item'):
            _, details = exp.find_element_by_class_name("pvs-entity").find_elements_by_xpath("*")
            details = details.find_elements_by_xpath("*")
            details_digest = details[0].find_element_by_xpath("*").find_elements_by_xpath("*")

            position = details_digest[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
            company = details_digest[1].find_element_by_tag_name("span").text
            if len(details_digest) > 2:
                date_range = details_digest[2].find_element_by_tag_name("span").text
            else:
                date_range = None
            if len(details_digest) > 3:
                location = details_digest[3].find_element_by_tag_name("span").text
            else:
                location = None
            details_text = details[1].text

            EXPERIENCE.append({'position': position, 'company': company, 
                               'date_range': date_range, 'location': location, 'details_text': details_text})
    except:
        pass

    # getting education
    try:
        browser.get(os.path.join(link, "details/education"))
        time.sleep(1)
        for edu in browser.find_elements_by_class_name('pvs-list__paged-list-item'):
            _, details = edu.find_element_by_class_name("pvs-entity").find_elements_by_xpath("*")
            details = details.find_elements_by_xpath("*")
            details_digest = details[0].find_element_by_xpath("*").find_elements_by_xpath("*")

            school = details_digest[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
            if len(details_digest) > 1:
                degree = details_digest[1].find_element_by_tag_name("span").text
            else:
                degree = None
            if len(details_digest) > 2:
                date_range = details_digest[2].find_element_by_tag_name("span").text
            else:
                date_range = None
            details_text = details[1].text

            EDUCATION.append({'school': school, 'degree': degree, 
                               'date_range': date_range, 'details_text': details_text})
    except:
        pass

    # getting recommendations
    try:
        browser.get(os.path.join(link, "details/recommendations"))
        time.sleep(1)
        for rec in browser.find_elements_by_class_name('pvs-list__paged-list-item'):
            _, details = rec.find_element_by_class_name("pvs-entity").find_elements_by_xpath("*")
            details = details.find_elements_by_xpath("*")
            details_digest = details[0].find_element_by_xpath("*").find_elements_by_xpath("*")

            person_name = details_digest[0].find_element_by_tag_name("span").find_element_by_tag_name("span").text
            person_position = details_digest[1].find_element_by_tag_name("span").text
            person_link = rec.find_element_by_class_name('optional-action-target-wrapper').get_attribute('href')
            date = details_digest[2].find_element_by_tag_name("span").text.split(',')[:-1]
            relation = details_digest[2].find_element_by_tag_name("span").text.split(',')[-1]
            details_text = details[1].text

            RECOMMENDATION.append({'person_name': person_name, 'person_position': person_position, 
                                   'person_link': person_link, 'date': date, 'details_text': details_text})
    except:
        pass

    result = {'NAME': NAME, 'TITLE': TITLE, 'LOCATION': LOCATION, 'ABOUT': ABOUT, 
              'EXPERIENCE': EXPERIENCE, 'EDUCATION': EDUCATION, 'RECOMMENDATION': RECOMMENDATION}

    return result

# scrape all the links and write in csv files
for link in linkedin_links:
    result = scrape(link, browser)
    df = pd.DataFrame.from_dict(result, orient='index')
    file_name = link.split('/')[-2] + '.csv'
    os.makedirs(output_root, exist_ok=True)
    output_dir = os.path.join(output_root, file_name)
    df.to_csv(output_dir)

browser.quit()



