from bs4 import BeautifulSoup as bs
from requests import get
import time
import schedule

def checkGitHub():
    url = 'https://github.com/savagecoder77'
    r = get(self.url)
    page = r.text
    soup = bs(page, 'html.parser')
    soup.findAll('rect', attrs={'class':'day'})

def job():
    pass

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every().day.at("21:30").do(run_threaded, job)
