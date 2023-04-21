import csv
import os
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

FILENAME = "people.csv"

# Authorization
def auth(driver, username, password):
    print(f"-------- auth --------")
    try:
        driver.get('https://linkedin.com')
        input_username = driver.find_element(By.NAME, "session_key")
        input_password = driver.find_element(By.NAME, "session_password")
        input_username.send_keys(username)
        input_password.send_keys(password)
        input_password.send_keys(Keys.ENTER)
    except Exception as err:
        print(err)
        driver.quit()


def scrape_companies(driver, size, max_page):
    print(f"-------- start: scrape_companies --------")
    industry_map = {"cryptocurrency": set(),
                    "energy": set(), "health": set(), "technology": set(), "research": set(),
                    "education": set(), "real estate": set(), "consultancy": set()
                    }

    for search_term in industry_map.keys():
        # search new term
        search_box = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        # filter by companies
        if "companies" not in driver.current_url:
            driver.find_element(By.XPATH, "//button[text()='Companies']").click()

        filters = []
        if "companySize" not in driver.current_url:
            # filter by company size
            driver.find_element(By.XPATH, "//button[text()='Company size']").click()
            # save size filters
            if size == SML:
                filters.append("label[for='companySize-B']")
            elif size == MED:
                filters.append("label[for='companySize-C']")
            elif size == LRG:
                filters.append("label[for='companySize-D']")
                filters.append("label[for='companySize-E']")
                filters.append("label[for='companySize-F']")
                filters.append("label[for='companySize-G']")
                filters.append("label[for='companySize-H']")
                filters.append("label[for='companySize-I']")

            # set size filters
            for fltr in filters:
                driver.find_element(By.CSS_SELECTOR, fltr).click()
            driver.find_element(By.XPATH, "//button[text()='Company size']").click()
            time.sleep(3)

        # filter by geography=US
        if "companyHqGeo" not in driver.current_url:
            driver.get(driver.current_url + '&companyHqGeo=%5B"103644278"%5D')

        # do work of scraping companies
        for i in range(1, max_page + 1):
            # grab all company links
            companies = driver.find_elements(By.CLASS_NAME, "app-aware-link ")
            for comp in companies:
                try:
                    # make sure link is a company link not random link
                    company_link = comp.get_attribute("href")
                    if "https://www.linkedin.com/company" in company_link:
                        industry_map[search_term].add(company_link)
                except Exception as exc:
                    print(exc)
                    continue

            # get url for next page by appending page=#
            if "page" not in driver.current_url:
                # case for page 1
                next_url = driver.current_url + "&page=2"
            else:
                # case for all subsequent pages
                next_url = driver.current_url.replace(f"page={i}", f"page={i+1}")

            # next page iteration
            driver.get(next_url)

        # # debug line per industry
        # print(f"-------- {search_term} --------")
        # print(industry_map)

    print(f"-------- end: scrape_companies --------")
    print(industry_map)
    return industry_map


def scrape_people(driver, industry_map):
    print(f"-------- start: scrape_people --------")
    company_map = {}
    for industry in industry_map.keys():
        for company in industry_map[industry]:
            try:
                company_people = company + 'people'
                driver.get(company_people)
                time.sleep(3)
                people_links = []
                while len(people_links) == 0:
                    people_links = driver.find_elements(By.CLASS_NAME, "app-aware-link ")
                for link in people_links:
                    if "miniProfile" in link.get_attribute("href"):
                        if company not in company_map:
                            company_map[company] = set()
                        else:
                            company_map[company].add(link.get_attribute("href"))
            except Exception as exc:
                print(exc)
                continue
            except KeyboardInterrupt as exc:
                print(exc)
                break

    print(f"-------- end: scrape_people --------")
    print(company_map)
    write_people(company_map, FILENAME)
    return


def message_people(driver, filename):
    people = read_people(filename)
    sent = {"sent": []}
    WAIT_TIME = 5
    MSG = "Hey, my name is Prince and I'm a co-founder at Lawracle. We help orgs identify public policy that affects " \
          "them quickly and effeciently. If we could help you or someone you know don't hesitate to reach out. Check " \
          "out our site at lawracle.co, thanks!"
    print(f"-------- start: message_people --------")
    # job_titles = []
    for person in people:
        try:
            driver.get(person)
            time.sleep(WAIT_TIME)
            txt_box = False
            while not txt_box:
                try:
                    txt_box = driver.find_element(By.ID, "custom-message")
                except Exception:
                    pass

            txt_box.send_keys(MSG)
            time.sleep(WAIT_TIME)
            sent["sent"].append(person)
            # TODO: filter this functionality to only certain positions
            # description = driver.find_element(By.XPATH, '//div[contains(@class, "text-body-medium") and
            # contains(@class, "break-words")]')
            # matches = [job for job in job_titles if job.lower() in description.lower()]
            # if len(matches) > 0:
        except Exception as exc:
            print(exc)
            continue
        except KeyboardInterrupt as exc:
            print(exc)
            break

    write_people(sent, "sent.csv")
    print(f"-------- end: message_people --------")
    return


def write_people(company_map, filename):
    with open(filename, 'w+', encoding='UTF8') as f:
        writer = csv.writer(f)
        for company in company_map.keys():
            for person in company_map[company]:
                writer.writerow([company, person])


def read_people(filename):
    people = []
    with open(filename, 'r', encoding='UTF8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            if row:
                people.append(row[1])
    return people


if __name__ == "__main__":
    SML = 10
    MED = 50
    LRG = 200
    MAX_PAGE = 10
    print("#############################################")
    print("Starting linkedin bot...")
    # set driver options
    chrome_options = Options()
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--window-size=1420,1080')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("--disable-notifications")
    # chrome_options.add_argument("--remote-debugging-port=9222")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option('useAutomationExtension', False)
    # chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
    # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
    # chrome_options.add_argument('user-agent={0}'.format(user_agent))
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    DRIVER.implicitly_wait(20)
    DRIVER.maximize_window()
    auth(DRIVER, "username", os.environ.get("LNK_PSW"))
    ind_map = scrape_companies(DRIVER, MED, MAX_PAGE)
    scrape_people(DRIVER, ind_map)
    message_people(DRIVER, FILENAME)
