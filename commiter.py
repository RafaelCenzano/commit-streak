from requests import get
import time
import json
import schedule
import config
import os
from smtplib import SMTP # smtplib for connection and sending of email
from email.mime.text import MIMEText # MIMEText for formatting
from email.mime.multipart import MIMEMultipart # MIMEMultipart changing sender
import threading

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

def send_email():
    sender_name = ('Commit-Streak <' + config.email_user + '>')
    msg = MIMEMultipart() # formatting
    msg['From'] = sender_name
    msg['To'] = config.recipient_email # input recipient email
    msg['Subject'] = 'Commit streak reminder' # input subject
    msg.attach(MIMEText('You have not made a commit on github today. If you do not commit by 11:30 we will make a single update','plain')) # add body
    message = msg.as_string() # format all text
    smtp_server = SMTP('smtp.gmail.com', 587) # connection to 587 port for gmail
    smtp_server.ehlo_or_helo_if_needed()
    smtp_server.starttls() #start connection
    smtp_server.ehlo_or_helo_if_needed()
    smtp_server.login(config.email_user, config.email_pass) # login with credentials
    smtp_server.sendmail(config.email_user, config.recipient_email, message) # send email
    smtp_server.quit() # quit connection
    print('Email Sent!') # done

def job():
    grand_total = 0

    user = 'savagecoder77'
    usrtotal = 0
    for repo in count_user_commits(user):
        print('Repo ' + str(repo['name']) + ' has ' + str(repo['num_commits']) + ' commits.')
        usrtotal += repo['num_commits']
    print('Total commits: ' + str(usrtotal))
    grand_total += usrtotal

    user = 'marvin-virtual-assistant'
    orgtotal = 0
    for repo in count_user_commits(user):
        print('Repo ' + str(repo['name']) + ' has ' + str(repo['num_commits']) + ' commits.')
        orgtotal += repo['num_commits']
    print('Total commits: ' + str(orgtotal))
    grand_total += orgtotal

    print(str(grand_total))
    return grand_total, usrtotal, orgtotal

def check(total, history):
    if total == history['original']['grand']:
        return True
    else:
        history['current']['grand'] = total
        return False

def job1():
    grand, usr, org = job()
    path_to_file = os.path.join('data','history.json')
    with open(path_to_file, 'r') as check_history:
        loaded_history = json.load(check_history)
    var = check(grand, loaded_history)
    if var == True:
        send_email()
        print('sent reminder')
    else:
        print('check complete everything in place')

def job2():
    grand, usr, org = job()
    path_to_file = os.path.join('data','history.json')
    with open(path_to_file, 'r') as check_history:
        loaded_history = json.load(check_history)
    var = check(grand, loaded_history)
    if var == True:
        print('commiting')
        f = open('commits.txt', 'w')
        f.write('/n' + str(os.urandom(64).decode('utf-8')))
        f.close()
        os.system('git add commits.txt\ngit commit -m "made an update for you"\ngit push')
        print('made a commit')
    else:
        print('check complete everything in place')
    with open(path_to_file, 'r') as check_history:
        loaded_history = json.load(check_history)
    loaded_history['current']['grand'] = loaded_history['current']['grand'] + 1
    loaded_history['current']['maintotal'] = loaded_history['current']['maintotal'] + 1
    loaded_history['original']['grand'] = loaded_history['current']['grand']
    loaded_history['original']['maintotal'] = loaded_history['current']['maintotal']
    loaded_history['original']['organizationtotal'] = loaded_history['current']['organizationtotal']
    with open(settings_path, 'w') as newjsonfile:
        json.dump(loaded_history, newjsonfile)

def job3():
    grand, usr, org = job()
    path_to_file = os.path.join('data','history.json')
    with open(path_to_file, 'r') as check_history:
        loaded_history = json.load(check_history)
    loaded_history['current']['grand'] = loaded_history['current']['grand'] + 1
    loaded_history['current']['maintotal'] = loaded_history['current']['maintotal'] + 1
    loaded_history['original']['grand'] = loaded_history['current']['grand']
    loaded_history['original']['maintotal'] = loaded_history['current']['maintotal']
    loaded_history['original']['organizationtotal'] = loaded_history['current']['organizationtotal']
    with open(settings_path, 'w') as newjsonfile:
        json.dump(loaded_history, newjsonfile)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    print('start')
    job_thread.start()

print('starting')
schedule.every().day.at("3:00").do(run_threaded, job1)
schedule.every().day.at("19:30").do(run_threaded, job1)
schedule.every().day.at("23:30").do(run_threaded, job2)

print('looping')
while True:
    schedule.run_pending()
    time.sleep(30)
