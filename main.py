from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
from config import gmail_user, gmail_password, odus_id, odus_password, currentSemesterBodyPath
import smtplib
import random

foundCourses = []
sent_from = gmail_user
to = [gmail_user]
body = 'Please check OdusPlus'
path = "\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--window-size=800,900")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
firstRun = True


def login():
    # URL changed because the old one "https://odusplus-ss.kau.edu.sa/" didn't work for the newer chromedriver
    driver.get('https://odusplus-ss.kau.edu.sa/PROD/twbkwbis.P_WWWLogin')
    username = driver.find_element(By.ID, 'userid')
    # Changed By.ID to By.NAME because the inputbox at least on my version does not have ID so I have to use the box name instead
    password = driver.find_element(By.NAME, 'password')
    username.send_keys(odus_id)
    password.send_keys(odus_password)
    # The old XPATH didn't work out with the newer URL or at least on my part.
    loginButtonPath = '//*[@id="Login"]/button'
    driver.find_element(By.XPATH, loginButtonPath).click()
    time.sleep(2)  # Time to load


login()
while True:
    driver.get('https://odusplus-ss.kau.edu.sa/PROD/ywsksinf.P_Display_All_Info')
    time.sleep(2)  # Time to load
    html_source = driver.page_source
    if '<img src="../wtlgifs/banner/login.jpg" border="0">' in html_source or 'تم اكتشاف محاولة دخول غير مسموح بها! الرجاء تسجيل الدخول مرة أخرى.' in html_source or 'تسجيل دخول جامعة الملك عبدالعزيز' in html_source:
        login()
        driver.get('https://odusplus-ss.kau.edu.sa/PROD/ywsksinf.P_Display_All_Info')
        time.sleep(2)  # Time to load
    GradesTable = driver.find_element(By.XPATH,currentSemesterBodyPath)
    rows = GradesTable.find_elements(By.XPATH,'./tr')
    iterRows = iter(rows)
    next(iterRows)
    for row in iterRows:
        courseCode = row.text.split()[0]+row.text.split()[1]
        grade = row.find_elements(By.XPATH,'./td')
        if grade[5].text != ' ':  # grade is not posted yet
            if courseCode not in foundCourses:
                print('New grade detected for '+courseCode)
                print('Time: '+str(datetime.now()))
                foundCourses.append(courseCode)                    
                if not firstRun:
                    subject = 'New grade detected on OdusPlus for '+courseCode
                    email_text = """\
From: %s
To: %s
Subject: %s
%s
                    """ % (sent_from, ", ".join(to), subject, body)
                    try:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.ehlo()
                        server.login(gmail_user, gmail_password)
                        server.sendmail(sent_from, to, email_text)
                        server.close()
                        print('Email sent!')
                    except:
                        print('Something went wrong...')
    firstRun = False
   # Change the rate of update here.
    timer = random.randint(90, 120)
    print(f'Sleeping for {timer} seconds')
    time.sleep(timer)
