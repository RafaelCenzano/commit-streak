from requests import get
import time
import json
import schedule
from config import *

def count_user_commits(user):
    r = get('https://api.github.com/users/' + user + '/repos')
    repos = json.loads(r.content)

    for repo in repos:
        if repo['fork'] is True:
            # skip it
            continue
        n = count_repo_commits(repo['url'] + '/commits')
        repo['num_commits'] = n
        yield repo


def count_repo_commits(commits_url, _acc=0):
    r = get(commits_url)
    commits = json.loads(r.content)
    n = len(commits)
    if n == 0:
        return _acc
    link = r.headers.get('link')
    if link is None:
        return _acc + n
    next_url = find_next(r.headers['link'])
    if next_url is None:
        return _acc + n
    # try to be tail recursive, even when it doesn't matter in CPython
    return count_repo_commits(next_url, _acc + n)


# given a link header from github, find the link for the next url which they use for pagination
def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]


def job():
    grand_total = 0

    user = 'savagecoder77'
    total = 0
    for repo in count_user_commits(user):
        print('Repo ' + str(repo['name']) + ' has ' + str(repo['num_commits']) + ' commits.')
        total += repo['num_commits']
    print('Total commits: ' + str(total))
    grand_total += total

    user = 'marvin-virtual-assistant'
    total = 0
    for repo in count_user_commits(user):
        print('Repo ' + str(repo['name']) + ' has ' + str(repo['num_commits']) + ' commits.')
        total += repo['num_commits']
    print('Total commits: ' + str(total))
    grand_total += total

    print(str(grand_total))
    return grand_total

def job1():
    bob = job()

def job2():
    bob = job()

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    print('start')
    job_thread.start()

#schedule.every().day.at("21:30").do(run_threaded, job1)
#schedule.every().day.at("24:30").do(run_threaded, job2)
job()
