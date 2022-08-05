import os
#os.system("pip install apprise")
import apprise
import time
import random
import traceback
#os.system("pip install RandomWords")
from random_words import RandomWords

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Optional
APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS", "")
if APPRISE_ALERTS:
    APPRISE_ALERTS = APPRISE_ALERTS.split(",")

points = -1

TERMS = ["define ", "explain ", "example of ", "how to pronounce ", "what is ", "what is the ", "what is the definition of ", "what is the example of ", "what is the pronunciation of ", "what is the synonym of ", "what is the antonym of ", "what is the hypernym of ", "what is the meronym of ","photos of "]


def login(EMAIL, PASSWORD, driver):
    driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(EMAIL)
    driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(Keys.ENTER)
    time.sleep(2)
    driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(Keys.ENTER)
    time.sleep(3)
    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()

def exploreSet(driver):
    print('\n\tDaily Explore starting...')
    p = driver.current_window_handle
    driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
    time.sleep(2)
    chwd = driver.window_handles
    driver._switch_to.window(chwd[1])
    try:
        time.sleep(5)
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        time.sleep(8)
        driver.refresh()
    except:
        driver.refresh()
        pass
    driver.close()
    driver._switch_to.window(p)
    driver.refresh()
    print('\n\tDaily Explore completed!')
    return


def dailyPoll(driver):
    print('\n\tDaily Poll starting...')
    driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
    time.sleep(2)
    p = driver.current_window_handle
    try:
        chwd = driver.window_handles
        driver._switch_to.window(chwd[1])
        driver.refresh()
        try:
            time.sleep(5)
            driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        except:
            driver.refresh()
            pass
        time.sleep(5)
        driver.find_element(By.XPATH, value='//*[@id="btoption0"]/div[2]/div[2]').click()
        time.sleep(8)
        print('\n\tDaily Poll completed!')
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
    except Exception as e:
        driver._switch_to.window(p)
        driver.refresh()
        pass
    time.sleep(5)
    return

# Currently does not work with correct answers
def dailyQuiz(driver):
    p = driver.current_window_handle
    print('\n\tDaily Quiz Starting...')
    driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
    time.sleep(4)
    chwd = driver.window_handles
    driver._switch_to.window(chwd[1])
    time.sleep(8)
    # //*[@id="slideexp6_950E60"] XPATH choice container
    try:
        time.sleep(5)
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        time.sleep(3)
        driver.refresh()
    except:
        driver.refresh()
        pass
    try:
        numberOfQuestions = driver.find_element(By.XPATH, value='//*[@id="QuestionPane0"]/div[2]').text.strip().split("of ")[1]
        numberOfQuestions = numberOfQuestions[:-1]
        for i in range(int(numberOfQuestions)):
            driver.find_element(By.CLASS_NAME, value='wk_OptionClickClass').click()
            time.sleep(8)
            driver.find_element(By.CLASS_NAME, value='wk_buttons').find_elements(By.XPATH, value='*')[0].send_keys(Keys.ENTER)
            time.sleep(5)
            print('\n\tDaily Quiz completed!')
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
        return
    except Exception as e:
        pass
    
    if (driver.find_elements(By.XPATH, value='//*[@id="rqStartQuiz"]') or driver.find_elements(By.CLASS_NAME, value='btOptions') or driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span')):
        try:
            driver.find_element(By.XPATH, value='//*[@id="rqStartQuiz"]').click()
        except:
            pass
        try:
            time.sleep(3)
            if (driver.find_elements(By.XPATH, value='//*[@id="rqHeaderCredits"]')):
                section = len(driver.find_element(By.XPATH, value='//*[@id="rqHeaderCredits"]').find_elements(By.XPATH, value='*'))
                for i in range(section):
                    choices = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span').text
                    choices = choices[-1]
                    print(choices)
                    try:
                        for i in range(int(choices)*3):
                            time.sleep(5)
                            option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{i}"]')
                            if (option.get_attribute('iscorrectoption') == 'True'):
                                option.click()
                    except Exception:
                        continue
                print('\n\tDaily Quiz completed!')
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                return

            elif (driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]')):
                numberOfQuestions = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]').text.strip().split("of ")[1]
                print(numberOfQuestions)
                for i in range(int(numberOfQuestions)):
                    driver.find_element(By.CLASS_NAME, value='btOptionCard').click()
                    time.sleep(13)
                print('\n\tDaily Quiz completed!')
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                return
        except Exception as e:
            print(e)
            pass
  

def getPoints(EMAIL, PASSWORD, driver):
    points = -1
    driver.implicitly_wait(3)
    #driver.get('https://rewards.microsoft.com/')
    driver.maximize_window()
    try:
        #driver.find_element(By.XPATH, '//*[@id="raf-signin-link-id"]').click()
        driver.get('https://rewards.microsoft.com/Signin?idru=%2F')
        login(EMAIL, PASSWORD, driver)
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        print(e)
        pass
    try:
        time.sleep(10)
        points = driver.find_element(By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span').text
        print(f'Email:\t{EMAIL}\n\tPoints:\t{points}')
    except Exception:
        pass
    return points


def main():
    points = -1
    rw = "Random"
    # Loop through all accounts doing edge and mobile searches
    rw = RandomWords()

    # LOGIN EXAMPLE:
    # "EMAIL:PASSWORD,EMAIL:PASSWORD"
    accounts = os.environ["LOGIN"].split(",")
    delay = 6

    # Loop through the array of accounts, splitting each string into an username and a password, then doing edge and mobile searches
    for x in accounts:
        import time

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # EXPERIMENTAL
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
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

        try:
            time.sleep(3)
            driver.find_element(By.XPATH, value='//*[@id="rx-user-status-action"]').click()
            time.sleep(7)
            PC = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if(int(PC[0]) < int(PC[1])):
                Number_PC_Search = int((int(PC[1]) - int(PC[0])) / 5)
                print(f'\tPC Searches Left:\t{Number_PC_Search}')
            else:
                Number_PC_Search = 0
                print(f'\tPC Searches Completed:\t{PC[0]}/{PC[1]}')
            if (int(PC[1]) > 50):
                MOBILE = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
                if (int(MOBILE[0]) < int(MOBILE[1])):
                    Number_Mobile_Search = int(
                        (int(MOBILE[1]) - int(MOBILE[0])) / 5)
                    print(f'\tMobile Searches Left:\t{Number_Mobile_Search}')
                else:
                    Number_Mobile_Search = 0
                    print(f'\tMobile Searches Completed:\t{MOBILE[0]}/{MOBILE[1]}')
            else:
                Number_Mobile_Search = 0
        except Exception as e:
            print(e)
            pass
        driver.find_element(By.XPATH, '//*[@id="modal-host"]/div[2]/button').click()
        #driver.get('https://rewards.microsoft.com/')
        print('\n\n')
        ranSets = False

        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
                exploreSet(driver)
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass

        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
                dailyPoll(driver)
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass
        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium" or driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") =="mee-icon mee-icon-HourGlass"):
                dailyQuiz(driver)
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass
        # Starts Edge Search Loop
        if (Number_PC_Search > 0 or Number_Mobile_Search > 0 or ranSets):
            alerts.notify(title=f'Bing Rewards Automation Starting', body=f'Email:\t{EMAIL}\nPoints:\t{points}\nCash Value:\t${points/1300}\n')
            if (Number_PC_Search > 0):
                rw = RandomWords()
                driver.get('https://www.bing.com/')
                try:
                    login(EMAIL, PASSWORD, driver)
                except Exception as e:
                    driver.get('https://www.bing.com/')
                    #print(e)
                    pass
                # First test search
                time.sleep(delay)
                first = driver.find_element(By.ID, value="sb_form_q")
                first.send_keys("test")
                first.send_keys(Keys.RETURN)
                # Main search loop
                for x in range(1, Number_PC_Search+1):
                    # Create string to send
                    value = random.choice(TERMS) + rw.random_word()

                    # Clear search bar
                    ping = driver.find_element(By.ID, value="sb_form_q")
                    ping.clear()

                    # Send random keyword
                    ping.send_keys(value)

                    # add delay to prevent ban
                    time.sleep(4)
                    try:
                        go = driver.find_element(By.ID, value="sb_form_go")
                        go.click()

                    except:
                        driver.find_element(By.ID, value="sb_form_go").send_keys(Keys.RETURN)
                        pass

                    # add delay to prevent ban
                    time.sleep(delay)
                    print(f'Doing {x} search out of {Number_PC_Search} this is {int(x/Number_PC_Search*100)} percent done.')
            driver.quit()

            if (Number_Mobile_Search > 0):
                rw = RandomWords()
                # Opens Mobile Driver
                mobile_emulation = {"deviceName": "Nexus 5"}
                chrome_options = webdriver.ChromeOptions()

                chrome_options = Options()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_experimental_option(
                    "mobileEmulation", mobile_emulation)
                # EXPERIMENTAL
                # chrome_options.add_argument("--disable-blink-features=AutomationControlled")

                driver = webdriver.Chrome(options=chrome_options)
                driver.implicitly_wait(4)
                driver.get(os.environ['URL'])

                driver.maximize_window()

                try:
                    driver.find_element(By.XPATH, value='//*[@id="mHamburger"]').click()
                    driver.find_element(By.XPATH, value='//*[@id="HBSignIn"]/a[1]').click()
                except Exception as e:
                    pass

                login(EMAIL, PASSWORD, driver)
                print(f"Account {EMAIL} logged in successfully! Auto search initiated.")
                driver.get('https://www.bing.com/')
                # Main search loop
                for x in range(1, Number_Mobile_Search + 1):
                    value = random.choice(TERMS) + rw.random_word()

                    # Clear search bar
                    ping = driver.find_element(By.ID, value="sb_form_q")
                    ping.clear()

                    # Send random keyword
                    ping.send_keys(value)

                    try:
                        # add delay to prevent ban
                        time.sleep(4)
                        go = driver.find_element_by_id("sb_form_go")
                        go.click()
                    except Exception:
                        ping.send_keys(Keys.ENTER)
                        pass
                    time.sleep(delay)

                    print(f'Doing {x} search out of {Number_Mobile_Search} this is {int(x/Number_Mobile_Search*100)} percent done.')

                print("Account [" + EMAIL + "] has completed mobile searches]")
                driver.quit()

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(3)
            points = getPoints(EMAIL, PASSWORD, driver)

            alerts.notify(title=f'Bing Rewards Automation Complete', body=f'Email:\t{EMAIL}\nPoints:\t{points}\nCash Value:\t${points/1300}\n')
            driver.quit()
        else:
            driver.quit()


def apprise_init():
    alerts = apprise.Apprise()
    # Add all services from .env
    for service in APPRISE_ALERTS:
        alerts.add(service)
    return alerts


alerts = apprise_init()

if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(21600)
        except Exception as e:
            print(f"EXCEPTION: {e}\n\nTRACEBACK: {traceback.format_exc()}")
            alerts.notify(title=f'Bing Rewards Failed!',
                          body=f'EXCEPTION:{e}\n\nTraceback:{traceback.format_exc()}\n\nAttempting to restart...')
            time.sleep(20)
            continue
