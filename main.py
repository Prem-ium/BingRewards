import os
from tkinter.tix import CELL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import random
import time
import math
import apprise
from random_words import RandomWords

apprise_alerts = os.environ.get("APPRISE_ALERTS", "").split(",")
CELL = 20
COMP = 34
# Functions


def apprise_init():
    alerts = apprise.Apprise()
    # Add all services from .env
    for service in apprise_alerts:
        alerts.add(service)
    return alerts


alerts = apprise_init()


def login(EMAIL, PASSWORD, driver):
    driver.find_element(
        By.XPATH, value='//*[@id="i0116"]').send_keys(EMAIL)
    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
    time.sleep(3)
    driver.find_element(
        By.XPATH, value='//*[@id="i0118"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
    time.sleep(3)
    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()


def mainLoop():
    rw = "Random"
    COMP, CELL = 34, 21
    # Loop through all accounts doing edge and mobile searches

    def getPoints(EMAIL, PASSWORD):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(3)
        driver.get('https://rewards.microsoft.com/')
        try:
            driver.find_element(
                By.XPATH, '//*[@id="raf-signin-link-id"]').click()
            login(EMAIL, PASSWORD, driver)
        except Exception as e:
            pass
        try:
            time.sleep(5)
            points = driver.find_element(
                By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span').text
            print(points)

            driver.find_element(
                By.XPATH, value='//*[@id="rx-user-status-action"]').click()
            PC = driver.find_element(
                By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if(int(PC[0]) < int(PC[1])):
                print('Needs more searching')
                COMP = (int(PC[1]) - int(PC[0])) / 5
                print(f'{COMP} more searches needed.')
            else:
                COMP = 0
                print(PC[0] + '/' + PC[1] + ': All PC searches complete.')

            MOBILE = driver.find_element(
                By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if (int(MOBILE[0]) < int(MOBILE[1])):
                print('Needs more searching')
                CELL = (int(MOBILE[1]) - int(MOBILE[0])) / 5
                print(f'{CELL} more searches needed.')
            else:
                CELL = 0
                print(MOBILE[0] + '/' + MOBILE[1] +
                      ': All mobile searches complete.')
        except Exception as e:
            print(e)
        driver.quit()
        return points
    rw = RandomWords()
    EMAIL = os.environ['EMAIL']
    PASSWORD = os.environ['PASS']
    accounts = [f"{EMAIL}:{PASSWORD}"]
    alerts.notify(title=f'Bing Rewards:',
                  body=f'Bing Automation Booting...\nPoints: {getPoints(EMAIL, PASSWORD)}')

    # numSearch is number of PC searches
    Number_PC_Search = COMP
    # numSearch1 is number of mobile searches
    Number_Mobile_Search = CELL

    delay = 3

    numAccounts = len(accounts)
    print("BingAutoSearch V2.0.0 will automatically run both computer and mobile searches on", end=" ")
    print(numAccounts, end=" ")
    print("accounts!")
    print("This process will take approimately", end=" ")
    time = (numAccounts*((Number_PC_Search+Number_Mobile_Search*delay)) + 46)/60

    # Loop through the array of accounts, splitting each string into an username and a password, then doing edge and mobile searches
    for x in accounts:
        import time
        # Grab username
        colonIndex = x.index(":")+1
        user = x[0:colonIndex-1]
        # Grab password
        lastIndex = len(x)
        pw = x[colonIndex:lastIndex]
        # Edge Searches(34 searches total)

        # Opens Edge Driver
        # PATH = "C:/Users/Capta/Documents/edgedriver_win64/msedgedriver.exe"
    # driver = webdriver.Edge(PATH)
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(3)
        try:
            url = os.environ['URL']
            driver.get(url)
            driver.maximize_window()
            login(EMAIL, PASSWORD, driver)
        except Exception as e:
            print(e)
            print(
                "Error: Could not log into account. Cross your pinky you're weren't disrespectfully BANNED.")
            driver.get('https://bing.com')

        # First test search
        time.sleep(3)
        first = driver.find_element_by_id("sb_form_q")
        first.send_keys("test")
        first.send_keys(Keys.RETURN)

        # Starts Edge Search Loop

        def search():

            # Main search loop
            for x in range(1, Number_PC_Search+1):
                # Create string to send
                value = 'define ' + rw.random_word()

                # Clear search bar
                ping = driver.find_element_by_id("sb_form_q")
                ping.clear()

                # Send random keyword
                ping.send_keys(value)

                # add delay to prevent ban
                time.sleep(1)
                go = driver.find_element_by_id("sb_form_go")
                go.click()

                # add delay to prevent ban
                time.sleep(delay)

                # Print progress after each search
                print("Doing ", end="")
                print(x, end="")
                print(" search out of ", end="")
                print(Number_PC_Search)
                percentDone = x/Number_PC_Search*100
                print("This is ", end="")
                print(percentDone, end="")
                print("% done.")
            print(
                "Account [" + user + "] has completed PC searches. Please close the window or complete the daily taskes!")
            if(Number_PC_Search > 0):
                search()
            else:
                print("Bing Account has no PC searches for the day.")

            # Mobile Searches (20 searches total)

            # Opens Mobile Driver
            mobile_emulation = {"deviceName": "Nexus 5"}
            chrome_options = webdriver.ChromeOptions()

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option(
                "mobileEmulation", mobile_emulation)

            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.implicitly_wait(3)
            driver.get("https://login.live.com/")
            driver.maximize_window()

            login(EMAIL, PASSWORD, driver)
            print(
                "Account [" + user + "] logged in successfully! Auto search initiated.")
            driver.get('https://www.bing.com/')

            # First test search
            time.sleep(3)
            first = driver.find_element_by_id("sb_form_q")
            first.send_keys("test")
            first.send_keys(Keys.RETURN)

        # Starts Mobile Search Loop

        def mobile():
            # I N P U T = = = = = N E E D E D = = = = = = =Input number of searches wanted in 'numSearch' or uncomment #numSearch to input while the code is running
            # numSearch = int(input("Please enter number of searches: "))

            # Main search loop
            for x in range(1, Number_Mobile_Search + 1):
                value = 'define ' + rw.random_word()

                # Clear search bar
                ping = driver.find_element_by_id("sb_form_q")
                ping.clear()

                # Send random keyword
                ping.send_keys(value)

                # add delay to prevent ban
                time.sleep(1)
                go = driver.find_element_by_id("sb_form_go")
                go.click()

                # add delay to prevent ban
                time.sleep(delay)

                # Print progress after each search
                print("Doing ", end="")
                print(x, end="")
                print(" search out of ", end="")
                print(Number_Mobile_Search)
                percentDone = x/Number_Mobile_Search*100
                print("This is ", end="")
                print(percentDone, end="")
                print("% done.")
            print("Account [" + user + "] has completed mobile searches]")
        if (Number_Mobile_Search > 0):
            mobile()
        else:
            print("Bing Account has no mobile searches for the day.")
        alerts.notify(title=f'Bing Rewards Successful',
                      body=f'Points:{getPoints(EMAIL, PASSWORD)}')


while True:
    try:
        COMP, CELL = 34, 21
        mainLoop()
        time.sleep(86400)
    except Exception as e:
        print(e)
        COMP, CELL = 34, 21
        print("Error. Restarting...")
        alerts.notify(title=f'Bing Rewards',
                      body='Bing Automation Failed! Restarting!')
        time.sleep(500)
        continue


# Activate main loop
mainLoop()
print("BingAutoSearch V 3.0.0 has successfully boosted points on all accounts!")
