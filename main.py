from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from datetime import datetime
from config import odus_id, gmail_user, gmail_password, odus_password, currentSemesterBodyPath
import smtplib

foundCourses = []
sent_from = gmail_user
to = [gmail_user]
body = 'Please check OdusPlus'
path = "\chromedriver.exe"
driver = webdriver.Chrome()  # Open the website
driver.get('https://odusplus-ss.kau.edu.sa/')

firstRun = True


def login():
    username = driver.find_element_by_id('userid')
    password = driver.find_element_by_id('password')
    username.send_keys(odus_id)
    password.send_keys(odus_password)
    loginButtonPath = '/html/body/div/div[2]/div/div[1]/div/form/button'
    driver.find_element_by_xpath(loginButtonPath).click()
    time.sleep(2)  # Time to load


login()
while True:
    driver.get('https://odusplus-ss.kau.edu.sa/PROD/ywsksinf.P_Display_All_Info')
    time.sleep(2)  # Time to load
    html_source = driver.page_source
    if '<img src="../wtlgifs/banner/login.jpg" border="0">' in html_source or 'تم اكتشاف محاولة دخول غير مسموح بها! الرجاء تسجيل الدخول مرة أخرى.' in html_source or 'تسجيل دخول جامعة الملك عبدالعزيز' in html_source:
        login()
    GradesTable = driver.find_element_by_xpath(currentSemesterBodyPath)
    rows = GradesTable.find_elements_by_xpath('./tr')
    iterRows = iter(rows)
    next(iterRows)
    for row in iterRows:
        courseCode = row.text.split()[0]+row.text.split()[1]
        grade = row.find_elements_by_xpath('./td')
        if grade[5].text != ' ':  # grade is not posted yet
            if courseCode not in foundCourses:
                print('New grade detected for '+courseCode)
                print('Time: '+str(datetime.now()))
                foundCourses.append(courseCode)
                subject = 'New grade detected on OdusPlus for '+courseCode
                email_text = """\
From: %s
To: %s
Subject: %s
%s
                """ % (sent_from, ", ".join(to), subject, body)
                if not firstRun:
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
    print('Sleeping for 15m')
    time.sleep(900)
