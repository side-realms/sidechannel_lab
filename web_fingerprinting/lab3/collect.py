from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time, os, glob
from urllib.parse import quote_plus

sites10 = open('sites.txt').read().splitlines()
os.makedirs('traces/closed', exist_ok=True)

opts = Options()
opts.headless = True
#opts.binary_location = '/usr/bin/firefox'
service = Service('/usr/local/bin/geckodriver')
profile = webdriver.FirefoxProfile()
opts.profile = profile

driver = webdriver.Firefox(service=service, options=opts)

BASE = 'file://' + os.getcwd() + '/index.html'
DOWNLOAD_DIR = os.path.expanduser('~/Downloads')

def collect(sites, outdir, repeats):
    for site in sites:
        label = site.replace('://','_').replace('/','_')
        for i in range(repeats):
            driver.get(f"{BASE}?target={quote_plus(site)}")
            driver.find_element(By.ID, 'collect').click()
            time.sleep(20)
            latest = max(glob.glob(f"{DOWNLOAD_DIR}/*.json"), key=os.path.getmtime)
            os.replace(latest, f"{outdir}/{label}_{i}.json")
            print(f"collected {outdir}/{label}_{i}.json")

collect(sites10, 'traces/closed', 300)

driver.quit()

