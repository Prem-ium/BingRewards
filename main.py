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

apprise_alerts = os.environ.get("APPRISE_ALERTS", "").split(",")
points = -1
def apprise_init():
    alerts = apprise.Apprise()
    # Add all services from .env
    for service in apprise_alerts:
        alerts.add(service)
    return alerts
alerts = apprise_init()


def login(EMAIL, PASSWORD, driver):
    driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(EMAIL)
    driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(Keys.ENTER)
    time.sleep(3)
    driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(Keys.ENTER)
    time.sleep(3)
    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()


def main():
    import time
    points = -1
    rw = "Random"
    # Loop through all accounts doing edge and mobile searches

    def getPoints(EMAIL, PASSWORD, driver):
        points = -1
        driver.implicitly_wait(3)
        driver.get('https://rewards.microsoft.com/')
        driver.maximize_window()
        try:
            driver.find_element(
                By.XPATH, '//*[@id="raf-signin-link-id"]').click()
            login(EMAIL, PASSWORD, driver)
        except Exception as e:
            print(e)
        try:
            time.sleep(7)
            points = driver.find_element(By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span').text
            print(points)
        except Exception:
            pass
        return points
    rw = RandomWords()
  
    # LOGIN EXAMPLE:
    # "EMAIL:PASSWORD,EMAIL:PASSWORD"
    accounts = os.environ["LOGIN"].split(",")
    delay = 3

    # Loop through the array of accounts, splitting each string into an username and a password, then doing edge and mobile searches
    for x in accounts:
        import time
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(4)

        # Grab email
        colonIndex = x.index(":")+1
        EMAIL = x[0:colonIndex-1]
        # Grab password
        lastIndex = len(x)
        PASSWORD = x[colonIndex:lastIndex]
        # Set default search amount
        Number_Mobile_Search = 20
        Number_PC_Search = 34
        # Retireve points before completing searches
        points = getPoints(EMAIL, PASSWORD, driver)
        alerts.notify(title=f'Bing Rewards {EMAIL}:',body=f'Bing Automation Booting...\nPoints: {points}')

        try:
            time.sleep(3)
            driver.find_element(By.XPATH, value='//*[@id="rx-user-status-action"]').click()
            time.sleep(7)
            PC = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if(int(PC[0]) < int(PC[1])):
                print('PC Needs more searching')
                Number_PC_Search = int((int(PC[1]) - int(PC[0])) / 5)
                print(f'{Number_PC_Search} more searches needed.')
            else:
                Number_PC_Search = 0
                print(PC[0] + '/' + PC[1] + ': All PC searches complete.')
                
            MOBILE = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if (int(MOBILE[0]) < int(MOBILE[1])):
                print('Mobile Needs more searching')
                Number_Mobile_Search = int((int(MOBILE[1]) - int(MOBILE[0])) / 5)
                print(f'{Number_Mobile_Search} more searches needed.')
            else:
                Number_Mobile_Search = 0
                print(MOBILE[0] + '/' + MOBILE[1] + ': All mobile searches complete.')
        except Exception as e:
            print(e)
            pass
        # Starts Edge Search Loop

        if (Number_PC_Search > 0):
            driver.get(os.environ['URL'])
            try:
                login(EMAIL, PASSWORD, driver)
            except Exception as e:
                driver.get('https://www.bing.com/')
                print(e)
                pass
            # First test search
            time.sleep(3)
            first = driver.find_element(By.ID, value = "sb_form_q")
            first.send_keys("test")
            first.send_keys(Keys.RETURN)
            # Main search loop
            for x in range(1, Number_PC_Search+1):
                # Create string to send
                value = 'define ' + rw.random_word()

                # Clear search bar
                ping = driver.find_element(By.ID, value = "sb_form_q")
                ping.clear()

                # Send random keyword
                ping.send_keys(value)

                # add delay to prevent ban
                time.sleep(4)
                go = driver.find_element(By.ID, value = "sb_form_go")
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
        driver.quit()

        if (Number_Mobile_Search > 0):
            # Opens Mobile Driver
            mobile_emulation = {"deviceName": "Nexus 5"}
            chrome_options = webdriver.ChromeOptions()

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(4)
            driver.get(os.environ['URL'])
          
            driver.maximize_window()

            
            try:
                driver.find_element(By.XPATH, value='//*[@id="mHamburger"]').click()
                driver.find_element(By.XPATH, value='//*[@id="HBSignIn"]/a[1]').click()
            except Exception as e:
                print(e)
                pass
                      
            login(EMAIL, PASSWORD, driver)
            print("Account [" + EMAIL + "] logged in successfully! Auto search initiated.")
            driver.get('https://www.bing.com/')
            # Main search loop
            for x in range(1, Number_Mobile_Search + 1):
                value = 'define ' + rw.random_word()

                # Clear search bar
                ping = driver.find_element(By.ID, value = "sb_form_q")
                ping.clear()

                # Send random keyword
                ping.send_keys(value)

                try:
                    # add delay to prevent ban
                    time.sleep(4)
                    go = driver.find_element_by_id("sb_form_go")
                    go.click()
                except Exception as e:
                    ping.send_keys(Keys.ENTER)
                    pass
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
            print("Account [" + EMAIL + "] has completed mobile searches]")
            driver.quit()
            
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(3)
        points = getPoints(EMAIL, PASSWORD, driver)
        
        alerts.notify(title=f'Bing Rewards {EMAIL} Successful', body=f'Points: {points}')
        driver.quit()
    time.sleep(21600)

    

if __name__ == "__main__":
  while True:
      try:
          main()
      except Exception as e:
          print(f"Error.\n{e}\nRestarting...")
          alerts.notify(title=f'Bing Rewards',body=f'Bing Automation Failed!\n{e}\nAttempting to restart...')
          time.sleep(500)
          continue

