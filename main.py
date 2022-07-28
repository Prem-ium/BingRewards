import os
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
os.system("pip install RandomWords")
from random_words import RandomWords
from keep_alive import keep_alive

keep_alive()


apprise_alerts = os.environ.get("APPRISE_ALERTS", "").split(",")
rw = "Random"
# Functions


def apprise_init():
    alerts = apprise.Apprise()
    # Add all services from .env
    for service in apprise_alerts:
        alerts.add(service)
    return alerts


alerts = apprise_init()


# Loop through all accounts doing edge and mobile searches
def mainLoop():
    import time

    def getPoints(EMAIL, PASSWORD):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(3)
        driver.get('https://rewards.microsoft.com/')
        try:
            driver.find_element(By.XPATH,
                                '//*[@id="raf-signin-link-id"]').click()
            login(EMAIL, PASSWORD, driver)
        except Exception as e:
            pass
        time.sleep(5)
        points = driver.find_element(
            By.XPATH,
            '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span'
        ).text
        print(points)
        driver.quit()
        return points

    def login(EMAIL, PASSWORD, driver):
        driver.find_element(By.XPATH,
                            value='//*[@id="i0116"]').send_keys(EMAIL)
        driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
        time.sleep(3)
        driver.find_element(By.XPATH,
                            value='//*[@id="i0118"]').send_keys(PASSWORD)
        driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
        time.sleep(3)
        driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()

    rw = RandomWords()
    EMAIL = os.environ['EMAIL']
    PASSWORD = os.environ['PASS']
    accounts = [f"{EMAIL}:{PASSWORD}"]
    alerts.notify(
        title=f'Bing Rewards:',
        body=f'Bing Automation Booting...\nPoints: {getPoints(EMAIL, PASSWORD)}'
    )
    # numSearch is number of PC searches
    numSearch = 34
    # numSearch1 is number of mobile searches
    numSearch1 = 21

    delay = 3

    numAccounts = len(accounts)
    print(
        "BingAutoSearch V2.0.0 will automatically run both computer and mobile searches on",
        end=" ")
    print(numAccounts, end=" ")
    print("accounts!")
    print("This process will take approimately", end=" ")
    time = (numAccounts * ((numSearch + numSearch1 * delay)) + 46) / 60
    print(time, end=" ")
    print("minutes!")

    # Loop through the array of accounts, splitting each string into an username and a password, then doing edge and mobile searches
    for x in accounts:
        import time
        # Grab username
        colonIndex = x.index(":") + 1
        user = x[0:colonIndex - 1]
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
                "Error: Could not log into account. Trying to search instead.")
            driver.get('https://bing.com')

        # First test search
        time.sleep(3)
        first = driver.find_element_by_id("sb_form_q")
        first.send_keys("test")
        first.send_keys(Keys.RETURN)

        # Starts Edge Search Loop

        def search():
            numSearch = 34

            # Main search loop
            for x in range(1, numSearch + 1):
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
                print(numSearch)
                percentDone = x / numSearch * 100
                print("This is ", end="")
                print(percentDone, end="")
                print("% done.")
            print(
                "Account [" + user +
                "] has completed PC searches. Please close the window or complete the daily taskes!"
            )

        search()
        # Mobile Searches (20 searches total)

        # Opens Mobile Driver
        mobile_emulation = {"deviceName": "Nexus 5"}
        chrome_options = webdriver.ChromeOptions()

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("mobileEmulation",
                                               mobile_emulation)

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.implicitly_wait(3)
        driver.get("https://login.live.com/")
        driver.maximize_window()

        login(EMAIL, PASSWORD, driver)
        print("Account [" + user +
              "] logged in successfully! Auto search initiated.")
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
            for x in range(1, numSearch1 + 1):
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
                print(numSearch1)
                percentDone = x / numSearch1 * 100
                print("This is ", end="")
                print(percentDone, end="")
                print("% done.")
            print("Account [" + user + "] has completed mobile searches]")

        mobile()
        alerts.notify(
            title=f'Bing Rewards',
            body=
            f'Bing Automation Successful!\nPoints:{getPoints(EMAIL, PASSWORD)}'
        )


while True:
    try:
        mainLoop()
        time.sleep(86400)
    except Exception as e:
        print(e)
        print("Error. Restarting...")
        alerts.notify(title=f'Bing Rewards',
                      body='Bing Automation Failed! Restarting!')
        time.sleep(500)
        continue
# Activate main loop
mainLoop()
print(
    "BingAutoSearch V 3.0.0 has successfully boosted points on all accounts!")
