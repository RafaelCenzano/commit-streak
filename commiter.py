import requests
import time
import schedule

def checkGitHub():
    pass

def job():
    pass

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every().day.at("9:30").do(run_threaded, job)
