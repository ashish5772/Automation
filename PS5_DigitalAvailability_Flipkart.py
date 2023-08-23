from bs4 import BeautifulSoup as bs
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
import ctypes
CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
CHROMEDRIVER_PATH = r'D:\Chromedriver\chromedriver.exe'
#WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
#chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH

driver = wd.Chrome(executable_path=CHROMEDRIVER_PATH,
                              chrome_options=chrome_options
                             )
while True:
    driver.get(r'https://www.flipkart.com/sony-playstation-5-cfi-1008b01r-825-gb-astro-s-playroom/p/itm8bf74f8d0b890')
    content = driver.page_source
    soup = bs(content)
    #print(soup)
    availability = soup.find("div", {"class": "_16FRp0"})
    if not any('Coming Soon' in s for s in str(availability).split('\n')):
        ctypes.windll.user32.MessageBoxW(0, "ps5 digital available on flipkart", "PS5 digital available Flipkart", 1)
        break
    else: 
        print('not available')