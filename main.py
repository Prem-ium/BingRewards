import os
import random
import traceback
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from dotenv import load_dotenv

# In case imports fail, retry using pip
# RandomWords
try:
    from random_words import RandomWords
except ImportError:
    os.system("pip install RandomWords")
    from random_words import RandomWords
   
# pytz
try:
    from pytz import timezone
except ImportError:
    os.system("pip install pytz")
    from pytz import timezone
# Load ENV
load_dotenv()

# LOGIN EXAMPLE:
# "EMAIL:PASSWORD,EMAIL:PASSWORD"
if not os.environ["LOGIN"]:
    raise Exception("LOGIN not set. Please enter your login information in .env variable 'LOGIN' in the following format: 'EMAIL:PASSWORD,EMAIL2:PASSWORD2,EMAIL3:PASSWORD3'")
else:
    ACCOUNTS = os.environ["LOGIN"].replace(" ", "").split(",")

# Check number of accounts (limit to 5 per IP address to avoid bans)
if (len(ACCOUNTS) > 5):
    raise Exception(f"You can only have 5 accounts per IP address. Using more increases your chances of being banned by Microsoft Rewards. You have {len(ACCOUNTS)} accounts within your LOGIN env variable. Please adjust it to have 5 or less accounts and restart the program.")

if not os.environ["URL"]:
    raise Exception("URL env variable not set. Please enter a login URL in .env variable 'URL' obtained from the sign in button of https://bing.com/")

TERMS = ["define ", "explain ", "example of ", "how to pronounce ", "what is ", "what is the ", "what is the definition of ",
         "what is the example of ", "what is the pronunciation of ", "what is the synonym of ",
        "what is the antonym of ", "what is the hypernym of ", "what is the meronym of ","photos of "]

# Optional Variables
# Whether to use the chromewebdriver or not
HANDLE_DRIVER = os.environ.get("HANDLE_DRIVER", "False")
if (HANDLE_DRIVER.lower() == "true"):
    HANDLE_DRIVER = True
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
else:
    HANDLE_DRIVER = False

# Whether to fully automate redemptions
AUTO_REDEEM = os.environ.get("AUTO_REDEEM", "False")
if (AUTO_REDEEM.lower() == "true"):
    AUTO_REDEEM = True

    GOAL = os.environ.get("GOAL", "amazon.com").lower()
else:
    AUTO_REDEEM = False

# Whether to use keep_alive.py
if (os.environ.get("KEEP_ALIVE", "False").lower() == "true"):
    from keep_alive import keep_alive
    keep_alive()

# Apprise Alerts
APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS", "")
if APPRISE_ALERTS:
    APPRISE_ALERTS = APPRISE_ALERTS.split(",")
    # Apprise
    try:
        import apprise
    except ImportError:
        os.system("pip install apprise")
        import apprise

# Get IPs if it's set in .env
wanted_ipv4 = os.environ.get("WANTED_IPV4")
wanted_ipv6 = os.environ.get("WANTED_IPV6")

# Get proxy settings from .env
# Note that we should set '' instead of None in case PROXY is not defined to prevent the proxies dict below from being invalid (which breaks our IP checker)
proxy = os.environ.get("PROXY", "")

# Populate proxy dictionary for requests
proxies = {"http": f"{proxy}", "https": f"{proxy}"}

# Configure timezone
TZ = timezone(os.environ.get("TZ", "America/New_York"))

# Whether or not to use a timer, and if so, what time to use
TIMER = os.environ.get("TIMER", "False")
if TIMER.lower() == "true":
    TIMER = True
    # Get start and end time, defaulting to 4:00am and 8:00pm
    START_TIME = float(os.environ.get("START_TIME", "4"))
    END_TIME = float(os.environ.get("END_TIME", "20"))

    # Make sure start and end times are valid, otherwise switch them
    if START_TIME > END_TIME:
        print("Start time must be before end time, switching times...")
        temp = START_TIME
        START_TIME = END_TIME
        END_TIME = temp
else:
    TIMER = False
# Import bot name from .env
BOT_NAME = os.environ.get("BOT_NAME", "Bing Rewards Automation")
# Methods
def apprise_init():
    if APPRISE_ALERTS:
        alerts = apprise.Apprise()
        # Add all services from .env
        for service in APPRISE_ALERTS:
            alerts.add(service)
        return alerts
          
def get_current_ip(type, proxies):
    # try with icanhazip.com
    try:
        current_ip = (
            (requests.get(f"https://ip{type}.icanhazip.com", proxies=proxies)).text
        ).strip("\n")
        return current_ip
    except requests.ConnectionError:
        print(f"Unable to get IP{type} address")
        if type == "v4":
            # Send message to console and apprise alert if configured
            print(f"Failed to connect to icanhazip.com over {type}. Is there a problem with your network?")
            if APPRISE_ALERTS:
                alerts.notify(
                    title=f"Failed to connect to icanhazip.com over {type}",
                    body=f"Is there a problem with your network?"
                )
            # Wait some time (to prevent Docker containers from constantly restarting)
            sleep(300)
            raise Exception(
                f"Failed to connect to icanhazip.com over {type}. Is there a problem with your network?")
        if type == "v6":
            # We can just fail softly if this error occurs with v6
            # Note that a ConnectionError is raised if a v4-only host tries to connect to a v6 site
            # We can make this fail hard once v6 is actually widely available....
            return None
    except Exception as e:
        # Catch all other errors
        # Send message to console and apprise alert if configured
        print(
            f"An exception occurred while trying to get your current IP address: {e}"
        )
        if APPRISE_ALERTS:
            alerts.notify(
                title=f"An exception occurred while trying to get your current IP address",
                body=f"{e}"
            )
        # Wait some time (to prevent Docker containers from constantly restarting)
        sleep(60)
        raise Exception

def check_ip_address():
    # Compares desired IP address with actual external IP address
    # Print current IPv4 and check IPv6
    current_ipv4 = get_current_ip("v4", proxies)
    print(f"Current IPv4 Address: {current_ipv4}")
    current_ipv6 = get_current_ip("v6", proxies)
    if current_ipv6:
        print(f"Current IPv6 Address: {current_ipv6}")
    # If declared in .env, check the IPv4 address
    if wanted_ipv4:
        # Raise exception if they don't match, otherwise print success and continue
        if wanted_ipv4 != current_ipv4:
            # Send message to console and apprise if configured
            print(f"IPv4 addresses do not match. Wanted {wanted_ipv4} but got {current_ipv4}")
            if APPRISE_ALERTS:
                alerts.notify(title=f'IPv4 Address Mismatch', 
                    body=f'Wanted {wanted_ipv4} but got {current_ipv4}')
            raise Exception(f"IPv4 addresses do not match. Wanted {wanted_ipv4} but got {current_ipv4}"
            )
        else:
            print("IPv4 addresses match!")
    # If declared in .env, check the IPv6 address
    if wanted_ipv6 and current_ipv6:
        # Raise exception if they don't match, otherwise print success and continue
        if wanted_ipv6 != current_ipv6:
            # Send message to console and apprise if configured
            print(f"IPv6 addresses do not match. Wanted {wanted_ipv6} but got {current_ipv6}")
            if APPRISE_ALERTS:
                alerts.notify(title=f'IPv6 Address Mismatch', 
                    body=f'Wanted {wanted_ipv6} but got {current_ipv6}')
            raise Exception(
                f"IPv6 addresses do not match. Wanted {wanted_ipv6} but got {current_ipv6}"
            )
        else:
            print("IPv6 addresses match!")
    print()

def wait():
    currentHour = datetime.datetime.now(TZ).hour
    if not (currentHour >= START_TIME and currentHour <= END_TIME):
        range = (START_TIME-currentHour) if (currentHour < START_TIME) else ((24 - currentHour) + START_TIME)
        print(f'Timer is enabled.\nStart Time: {START_TIME}.\nEnd Time: {END_TIME}.\n\nCurrent time: {currentHour}.\nCurrent time is not within range. Sleeping for {range} hours.')
        sleep((range) * 3600)
    return

def login(EMAIL, PASSWORD, driver):
    # Find email and input it
    try:
        driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(EMAIL)
        driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(Keys.ENTER)
    except:
        try:
            username_field = driver.find_element(By.XPATH, value='//*[@id="i0116"]')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(username_field)
            )
            username_field.send_keys(EMAIL)
            username_field.send_keys(Keys.ENTER)
        except:
            return False
    sleep(random.uniform(2, 4))
    # Check if personal/work prompt is present
    try:
        message = driver.find_element(By.XPATH, value='//*[@id="loginDescription"]').text
        if message.lower() == "it looks like this email is used with more than one account from microsoft. which one do you want to use?":
            try:
                personal = driver.find_element(By.XPATH, value='//*[@id="msaTileTitle"]')
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(personal)
                )
                personal.click()
                sleep(random.uniform(2, 4))
            except:
                print(f'Personal/Work prompt was present for account {EMAIL} but unable to get past it.')
                return False
    except:
        pass
    # Find password and input it
    try:
        driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(PASSWORD)
        driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(Keys.ENTER)
    except:
        try:
            password_field = driver.find_element(By.XPATH, value='//*[@id="i0118"]')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(password_field)
            )
            password_field.send_keys(PASSWORD)
            password_field.send_keys(Keys.ENTER)
        except:
            print(f'Unable to find password field for account {EMAIL}')
            return False
    sleep(random.uniform(3, 6))
    try:
        driver.find_element(By.XPATH, value='//*[@id="iNext"]').click()
    except:
        pass
    try:
        driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
        return True
    except:
        try:
            message = driver.find_element(By.XPATH, value='//*[@id="StartHeader"]').text
            if message.lower() == "your account has been locked":
                print(f"uh-oh, your account {EMAIL} has been locked by Microsoft!")
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account Locked!', 
                        body=f'Your account {EMAIL} has been locked! Sign in and verify your account.\n\n...')
                return False
        except NoSuchElementException as e:
            pass
        try:
            message = driver.find_element(By.XPATH, value='//*[@id="iPageTitle"]').text
            if message.lower() == "help us protect your account":
                print(f"uh-oh, your account {EMAIL} will need to manually add an alternative email address!\nAttempting to skip in 1 minute, if possible...")
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account Secuirity Notice!', 
                        body=f'Your account {EMAIL} requires you to add an alternative email address or a phone number!\nPlease sign in and add one to your account.\n\n\nAttempting to skip, if still possible...')
                sleep(60)
                driver.find_element(By.XPATH, value='//*[@id="iNext"]').click()
        except Exception as e:
            print(e)
            try:
                sleep(2)
                driver.find_element(By.XPATH, value='//*[@id="iNext"]').click()
            except:
                try:
                    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
                except:
                    driver.find_element(By.XPATH, value='//*[@id="iShowSkip"]').click()
            finally:
                driver.get('https://rewards.microsoft.com/')
        return True

def completeSet(driver):
    sleep(random.uniform(10, 15))
    try:
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        sleep(8)
    except:
        pass
    finally:
        driver.refresh()
    return

def completePoll(driver):
    try:
        driver.refresh()
        try:
            sleep(random.uniform(3, 5))
            driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        except:
            driver.refresh()
            pass
        sleep(random.uniform(2, 7))
        driver.find_element(By.XPATH, value='//*[@id="btoption0"]/div[2]/div[2]').click()
        sleep(8)
        print('\tPoll completed!')
    except:
        pass
    sleep(3)
    return

# TODO: Clean up code
def completeQuiz(driver):
    sleep(random.uniform(7, 14))
    try:
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        sleep(4)
    except:
        pass
    driver.refresh()
    try:
        numberOfQuestions = (driver.find_element(By.XPATH, value='//*[@id="QuestionPane0"]/div[2]').text.strip().split("of ")[1])[:-1]
        for i in range(int(numberOfQuestions)):
            driver.find_element(By.CLASS_NAME, value='wk_OptionClickClass').click()
            sleep(8)
            driver.find_element(By.CLASS_NAME, value='wk_buttons').find_elements(By.XPATH, value='*')[0].send_keys(Keys.ENTER)
            sleep(5)
        print('\tQuiz completed!')
        return
    except Exception as e:
        pass
    
    if (driver.find_elements(By.XPATH, value='//*[@id="rqStartQuiz"]') or driver.find_elements(By.CLASS_NAME, value='btOptions') or driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span') or driver.find_elements(By.CLASS_NAME, value='rq_button')):
        try:
            start = driver.find_element(By.XPATH, value='//*[@id="rqStartQuiz"]')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(start)
            )
            start.click()
        except Exception as e:
            try:
                driver.find_element(By.XPATH, value='//*[@id="rqStartQuiz"]').click()
            except:
                pass
        try:
            sleep(3)
            if (driver.find_elements(By.XPATH, value='//*[@id="rqHeaderCredits"]')):
                section = len(driver.find_element(By.XPATH, value='//*[@id="rqHeaderCredits"]').find_elements(By.XPATH, value='*'))
                try:
                    for i in range(section):
                        try:
                            choices = len(driver.find_element(By.CLASS_NAME, value='rqCredits').find_elements(By.XPATH, value='*'))
                            for i in range(choices * 2):
                                buttons = len(driver.find_elements(By.CLASS_NAME, value='rq_button'))
                                sleep(5)
                                option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{random.randint(0, buttons - 1)}"]')
                                option.click()
                                sleep(10)
                                try:
                                    while (driver.find_element(By.XPATH, value='//*[@id="rqAnsStatus"]').text.lower() == 'oops, try again!'):
                                        option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{random.randint(0, buttons - 1)}"]')
                                        option.click()
                                        sleep(5)
                                except:
                                    pass
                                if ("great job - you just earned" in driver.find_element(By.XPATH, value='//*[@id="quizCompleteContainer"]/div/div[1]').text.lower()):
                                    sleep(5)
                                    break
                            print('\tQuiz completed!')
                            return
                        except:
                            pass
                except:
                    pass
                for i in range(section):
                    try:
                        choices = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span').text
                        choices = int(choices[-1]) - int(choices[0])
                    except:
                        choices = len(driver.find_element(By.CLASS_NAME, value='rqCredits').find_elements(By.XPATH, value='*'))
                    try:
                        for i in range(choices * 2):
                            sleep(5)
                            option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{i}"]')
                            if (option.get_attribute('iscorrectoption') == 'True'):
                                option.click()
                    except Exception:
                        continue
                print('\tQuiz completed!')
                return

            elif (driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]')):
                numberOfQuestions = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]').text.strip().split("of ")[1]
                for i in range(int(numberOfQuestions)):
                    driver.find_element(By.CLASS_NAME, value='btOptionCard').click()
                    sleep(13)
                print('\tQuiz completed!')
                return
        except Exception as e:
            print(e)
            pass

def guessTask(driver, p = "False"):
    try:
        if p.lower() == "false":
            p = driver.window_handles[len(driver.window_handles) - 1]
    except:
        pass
    try:
        completeQuiz(driver)
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
        return True
    except:
        pass
    try:
        completeSet(driver)
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
        return True
    except:
        pass
    try:
        completePoll(driver)
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
        return True
    except:
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
        return False
def punchcard(driver):
    try:
        driver.get('https://rewards.microsoft.com/')
        sleep(5)
        quests = driver.find_elements(By.CLASS_NAME, value='clickable-link')
        links = []
        for quest in quests:
            links.append(quest.get_attribute('href'))

        for link in links:
            driver.get(link)
            sleep(random.uniform(1, 3))
            try:
                message = driver.find_element(By.XPATH, '//*[@id="rewards-dashboard-punchcard-details"]/div[2]/div[2]/div[4]').text
                message2 = driver.find_element(By.XPATH, '//*[@id="rewards-dashboard-punchcard-details"]/div[2]/div[2]/div[2]').text
                if message.lower() == 'congratulations!' or "rent" in message2.lower() or "buy" in message2.lower():
                    continue
            except:
                pass
            p = driver.current_window_handle
            sleep(random.uniform(1, 3))
            try:
                driver.find_element(By.XPATH, value='//*[@id="rewards-dashboard-punchcard-details"]/div[2]/div[2]/div[7]/div[3]/div[1]/a/b').click()
            except:
                sleep(5)
                offers = driver.find_elements(By.CLASS_NAME, value = 'offer-cta')
                offers[0].find_element(By.CLASS_NAME, value = 'btn').click()
            chwd = driver.window_handles
            p = driver.current_window_handle
            if (chwd[1]):
                driver._switch_to.window(chwd[1])
            
            try:
                guessTask(driver, p)
                sleep(random.uniform(3, 5))
            except:
                sleep(random.uniform(3, 5))
                pass
    except Exception as e:
        print(traceback.format_exc())
        pass

def completeMore(driver):
    ran = False
    driver.get('https://rewards.microsoft.com/')
    try:
        count = len(driver.find_elements(By.CLASS_NAME, 'ds-card-sec')) - 6
        for i in range(count):
            i+=1
            try:
                element = driver.find_element(By.XPATH, value=f'/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-more-activities-card/mee-card-group/div/mee-card[{i}]')
                class_name = element.find_element(By.XPATH, value=f'/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-more-activities-card/mee-card-group/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a/mee-rewards-points/div/div/span[1]').get_attribute('class')

                if (class_name == "mee-icon mee-icon-AddMedium" or class_name == "mee-icon mee-icon-HourGlass"):
                    assign = driver.find_element(By.XPATH, value=f'//*[@id="more-activities"]/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a')
                    p = driver.current_window_handle
                    assign.click()
                    try:
                        driver.find_element(By.XPATH, value='//*[@id="legalTextBox"]/div/div/div[3]/a').click()
                    except:
                        pass
                    chwd = driver.window_handles
                    if (chwd[1]):
                        driver._switch_to.window(chwd[1])
                        try:
                            ran = guessTask(driver, p)
                        except:
                            print(traceback.format_exc())
                            pass
                        finally:
                            sleep(5)
                            driver.refresh()
                            sleep(5)
                    else:
                        driver.get('https://rewards.microsoft.com/')
            except:
                continue
    except Exception as e:
        print(traceback.format_exc())
        pass
    return ran

# TODO: Clean up code
def dailySet(driver):
        ranSets = False
        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
                p = driver.current_window_handle
                driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
                chwd = driver.window_handles
                driver._switch_to.window(chwd[1])
                completeSet(driver)
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass

        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
                p = driver.current_window_handle
                driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
                chwd = driver.window_handles
                driver._switch_to.window(chwd[1])
                completePoll(driver)
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass
        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium" or driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") =="mee-icon mee-icon-HourGlass"):
                p = driver.current_window_handle
                driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
                chwd = driver.window_handles
                driver._switch_to.window(chwd[1])
                completeQuiz(driver)
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass

        return ranSets

def checkStreaks(driver, EMAIL):
    try:
        driver.get('https://rewards.microsoft.com/')
        bonusNotification = driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-daily-set-section/div/mee-rewards-streak/div/div[2]/mee-rich-paragraph/p/b').text
        if bonusNotification is not None and 'Awesome!' in bonusNotification:
            print(f'\t{bonusNotification} for a streak bonus!\n')
            return bonusNotification
        else:
            bonusNotification = f"{driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/mee-rewards-user-status/div/div/div/div/div[3]/div[3]/mee-rewards-user-status-item/mee-rewards-user-status-streak/div/div/div/div/div/p[1]/mee-rewards-counter-animation').text} Days Streak!\n{driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-daily-set-section/div/mee-rewards-streak/div/div[2]/mee-rich-paragraph/p').text}"

            if len(bonusNotification) > 5:
                return bonusNotification
    except:
        return "N/A"
    return "N/A"

def getDriver(isMobile = False):
    try:
        if not HANDLE_DRIVER:
            chrome_options = Options()
        else:
            chrome_options = webdriver.ChromeOptions()

        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
            print(f"Set Chrome proxy to {proxy}")

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        if (isMobile):   
            mobile_emulation = {"deviceName": "Nexus 5"}
            chrome_options.add_experimental_option(
                "mobileEmulation", mobile_emulation)
        else:
            # Set to edge user agent if not mobile
            user_agent = "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/64.0.3282.140 safari/537.36 edge/18.17763"
            chrome_options.add_argument(f'user-agent={user_agent}')

        if not HANDLE_DRIVER:
            driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(cache_valid_range=30).install()),
                options=chrome_options)
    except:
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Driver Error', body=f'Error creating driver for {BOT_NAME}\n\n...')
        print(f'{traceback.format_exc()}\n\nAttempting to retry...\n\n')
        sleep(100)
        return getDriver(isMobile)
    driver.maximize_window()
    return driver

def redeem(driver, EMAIL):
    driver.get("https://rewards.microsoft.com/")
    try:
        element = driver.find_element(By.XPATH, value = '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/div/a/span/ng-transclude')
        setG = element.text
        if ("set goal" in setG.lower()):
            element.click()
            sleep(3)
            elements = driver.find_elements(By.CLASS_NAME,"c-image")
            for e in elements:
                if (GOAL in e.get_attribute("alt").lower()):
                    print('\tGoal set!')
                    e.click()
                    break
    except:
        pass
    finally:
        driver.get("https://rewards.microsoft.com/")
    try:
        position = driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/p').text.replace(" ", "").split("/")
        points = int(position[0].replace(",", ""))
        total = int(position[1].replace(",", ""))

        goal = driver.find_element(By.XPATH, value = '//*[@id="dashboard-set-goal"]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/h3').text
        print(f'\t{goal}')

        if (points < total):
            print(f"\t{total - points} points left to redeem your goal!")
            return f'\nPoints Remaining until {goal} Redeemption:\t{total - points} (${round((total - points) / 1300, 3)})\n'
        elif(points >= total):
            print("\tPoints are ready to be redeemed!\n\tIf this is the first time, manual SMS verification is required.")
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into an exception trying to redeem\n{traceback.format_exc()}\n"
    try:
        try:
            driver.find_element(By.XPATH, value = '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/div/a[1]/span/ng-transclude').click()
            sleep(random.uniform(2, 4))
        except:
            sleep(random.uniform(3, 5))
            driver.find_element(By.XPATH, value = '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/div/a[1]').click()
        try:
            url = driver.current_url
            url = url.split('https://rewards.microsoft.com/redeem/')
            id = url[1]
            try:
                driver.find_element(By.XPATH, value = f'//*[@id="redeem-pdp_{id}"]').click()
                sleep(random.uniform(3, 5))
            except:
                driver.find_element(By.XPATH, value = f'//*[@id="redeem-pdp_{id}"]/span[1]').click()
            try:
                driver.find_element(By.XPATH, value = '//*[@id="redeem-checkout-review-confirm"]').click()
                sleep(random.uniform(3, 5))
            except:
                driver.find_element(By.XPATH, value = '//*[@id="redeem-checkout-review-confirm"]/span[1]').click()
        except Exception as e:
            print(traceback.format_exc())
            driver.get("https://rewards.microsoft.com/")
            return f"Ran into an exception trying to redeem\n{traceback.format_exc()}\n"
        # Handle phone verification landing page
        try:
            veri = driver.find_element(By.XPATH, value = '//*[@id="productCheckoutChallenge"]/form/div[1]').text
            if (veri.lower() == 'phone verification'):
                print("\tPhone verification required!")

                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Phone Verification Required', body=f'{EMAIL} has enough points for redeeming your goal, but needs to verify phone number for first reward.\nPlease verify your phone number.\nNext redemption will be automatic, if enabled.\n\n...')
                print('\tSleeping for a bit to allow manual verification...')
                sleep(300)
                driver.get("https://rewards.microsoft.com/")
                return f"Phone Verification Required for {EMAIL}"
        except:
            pass
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Reward Redeemed', body=f'{EMAIL}\'s Points have been redeemed for the set goal!\n\n...')
        return f"\n{EMAIL} Points Redeemed"
    except Exception as e:
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Redeem Error', body=f'An error occured trying to auto-redeem for: {EMAIL}\n\n{traceback.format_exc()}\n\n...')
        print(e)
        return f"\tRan into an exception trying to redeem\n{traceback.format_exc()}\n"

def getPoints(EMAIL, PASSWORD, driver):
    points = -1
    driver.implicitly_wait(5)
    sleep(random.uniform(3, 5))
    try:
        driver.get('https://rewards.microsoft.com/Signin?idru=%2F')
        if not login(EMAIL, PASSWORD, driver):
            return -404
        # If it's the first sign in, join microsoft rewards
        if driver.current_url == 'https://rewards.microsoft.com/welcome':
            try:
                join_rewards = driver.find_element(By.XPATH, value='//*[@id="start-earning-rewards-link"]')
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(join_rewards)
                )
                join_rewards.click()
                print(f'Joined microsoft rewards on account {EMAIL}')
            except:
                try:
                    driver.find_element(By.XPATH, value='//*[@id="start-earning-rewards-link"]').click()
                    print(f'Joined microsoft rewards on account {EMAIL}')
                except:
                    print(traceback.format_exc())
                    print("Got rewards welcome page, but couldn't join rewards.")
                    return -404
            try:
                if driver.current_url == 'https://rewards.microsoft.com/welcometour':
                    driver.find_element(By.XPATH, value='//*[@id="welcome-tour"]/mee-rewards-slide/div/section/section/div/a[2]').click()
            except:
                driver.get('https://rewards.microsoft.com/')
        if driver.title.lower() == 'rewards error':
            sleep(random.uniform(2, 4))
            driver.get('https://rewards.microsoft.com/')
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        print(e)
        pass
    finally:
        sleep(random.uniform(8, 20))
   
    try:
        points = driver.find_element(By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span').text.strip().replace(',', '')
        return int(points)
    except:
        points = driver.find_element(By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[2]/div[2]/span').text.strip().replace(',', '')
        pass
        return int(points)

def PCSearch(driver, EMAIL, PASSWORD, PC_SEARCHES):
    rw = RandomWords()
    driver.get(os.environ['URL'])
    try:
        login(EMAIL, PASSWORD, driver)
    except:
        pass
    try:
        driver.find_element(By.XPATH, value='//*[@id="mHamburger"]').click()
        driver.find_element(By.XPATH, value='//*[@id="HBSignIn"]/a[1]').click()
    except Exception:
        pass
    finally:
        driver.get('https://www.bing.com/')

    try:
        driver.find_element(By.ID, 'id_l').click()
        sleep(2)
        driver.refresh()
    except:
        pass

    # First test search
    sleep(random.uniform(1, 6))
    first = driver.find_element(By.ID, value="sb_form_q")
    first.send_keys("test")
    first.send_keys(Keys.RETURN)

    # Main search loop
    for x in range(1, PC_SEARCHES+1):
        sleep(random.uniform(1, 6))
        # Create string to send
        value = random.choice(TERMS) + rw.random_word()

        # Clear search bar
        ping = driver.find_element(By.ID, value="sb_form_q")
        ping.clear()

        # Send random keyword
        ping.send_keys(value)

        # add delay to prevent ban
        sleep(4)
        try:
            go = driver.find_element(By.ID, value="sb_form_go")
            go.click()

        except:
            driver.find_element(By.ID, value="sb_form_go").send_keys(Keys.RETURN)
            pass

        # add delay to prevent ban
        sleep(random.uniform(5, 25))
        print(f'\t{x} PC search of {PC_SEARCHES}. Now {int(x/PC_SEARCHES*100)}% done.')
    print(f'\n\t{EMAIL} PC Searches completed: {datetime.datetime.now(TZ)}\n')

def PC_Search_Helper(driver, EMAIL, PASSWORD, PC_SEARCHES):
    try:
        PCSearch(driver, EMAIL, PASSWORD, PC_SEARCHES)
    except Exception as e:
        print(traceback.format_exc())
        print('Attempting to restart PC search in 500 seconds')
        sleep(500)
        driver.quit()
        driver = getDriver()
        try:
            PC_SEARCHES, MOBILE_SEARCHES = updateSearches(driver)
            PCSearch(driver, EMAIL, PASSWORD, PC_SEARCHES)
        except Exception as e:
            print('PC search failed, again! Skipping PC search.')
        pass
    finally:
        driver.quit()

def MobileSearch(driver, EMAIL, PASSWORD, MOBILE_SEARCHES):
    rw = RandomWords()
    driver.implicitly_wait(4)
    driver.get(os.environ['URL'])

    try:
        driver.find_element(By.XPATH, value='//*[@id="mHamburger"]').click()
        driver.find_element(By.XPATH, value='//*[@id="HBSignIn"]/a[1]').click()
    except Exception:
        pass

    login(EMAIL, PASSWORD, driver)
    print(f"\n\tAccount {EMAIL} logged in successfully! Auto search initiated.\n")
    driver.get('https://www.bing.com/')
    
    # Main search loop
    for x in range(1, MOBILE_SEARCHES + 1):
        value = random.choice(TERMS) + rw.random_word()
        try:
            # Clear search bar
            ping = driver.find_element(By.ID, value="sb_form_q")
            ping.clear()

            # Send random keyword
            ping.send_keys(value)
        except:
            driver.get('https://www.bing.com/')
            sleep(7)
            # Clear search bar
            ping = driver.find_element(By.ID, value="sb_form_q").send_keys(value)
            pass
        try:
            go = driver.find_element(By.ID, value="sb_form_go")
            go.click()
        except Exception:
            ping.send_keys(Keys.ENTER)
            pass
        sleep(random.uniform(5, 25))
        print(f'\t{x} mobile search of {MOBILE_SEARCHES}. Now {int(x/MOBILE_SEARCHES*100)}% done.')
    print(f'\n\t{EMAIL} Mobile Searches completed: {datetime.datetime.now(TZ)}\n')

def Mobile_Search_Helper(EMAIL, PASSWORD, MOBILE_SEARCHES):
    driver = getDriver(True)
    try:
        MobileSearch(driver, EMAIL, PASSWORD, MOBILE_SEARCHES)
    except Exception as e:
        print(traceback.format_exc())
        print('Attempting to restart Mobile search in 500 seconds')
        sleep(500)
        driver.quit()
        driver = getDriver()
        PC_SEARCHES, MOBILE_SEARCHES = updateSearches(driver)
        driver.quit()
        driver = getDriver(True)
        try:
            MobileSearch(driver, EMAIL, PASSWORD, MOBILE_SEARCHES)
        except Exception as e:
            pass
        pass
    finally:
        driver.quit()
  
def updateSearches(driver):
    driver.get('https://rewards.microsoft.com/pointsbreakdown')
    
    PC_SEARCHES = 34
    MOBILE_SEARCHES = 24
    try:
        sleep(10)
        PC = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
        
        if (int(PC[0]) < int(PC[1])):
            PC_SEARCHES = int((int(PC[1]) - int(PC[0])) / 5)
            print(f'\tPC Searches Left:\t{PC_SEARCHES}')
        else:
            PC_SEARCHES = 0
            print(f'\tPC Searches Completed:\t{PC[0]}/{PC[1]}')

        if (int(PC[1]) > 50):
            MOBILE = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if (int(MOBILE[0]) < int(MOBILE[1])):
                MOBILE_SEARCHES = int((int(MOBILE[1]) - int(MOBILE[0])) / 5)
                print(f'\tMobile Searches Left:\t{MOBILE_SEARCHES}')
            else:
                MOBILE_SEARCHES = 0
                print(f'\tMobile Searches Completed:\t{MOBILE[0]}/{MOBILE[1]}')
        else:
            MOBILE_SEARCHES = 0
        try:
            driver.find_element(By.XPATH, '//*[@id="modal-host"]/div[2]/button').click()
        except:
            driver.get('https://rewards.microsoft.com/')
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        print(traceback.format_exc())
        pass
    finally:
        print()
        return PC_SEARCHES, MOBILE_SEARCHES

def runRewards():
    totalPointsReport = totalDifference = differenceReport = 0
    ranRewards = False
    loopTime = datetime.datetime.now(TZ)
    print(f'\nStarting Bing Rewards Automation:\t{loopTime}\n')
    for x in ACCOUNTS:
        driver = getDriver()

        # Grab email
        colonIndex = x.index(":")+1
        EMAIL = x[0:colonIndex-1]
        PASSWORD = x[colonIndex:len(x)]

        # Set default search amount
        PC_SEARCHES = 34
        MOBILE_SEARCHES = 20

        # Retireve points before completing searches
        points = getPoints(EMAIL, PASSWORD, driver)
        if (points == -404):
            driver.quit()
            continue
        print(f'Email:\t{EMAIL}\n\tPoints:\t{points}\n\tCash Value:\t${round(points/1300,3)}\n')

        PC_SEARCHES, MOBILE_SEARCHES = updateSearches(driver)
        
        recordTime = datetime.datetime.now(TZ)
        ranDailySets = dailySet(driver)
        ranMoreActivities = completeMore(driver)
        punchcard(driver)
 
        if AUTO_REDEEM:
            redeem(driver, EMAIL)

        if (PC_SEARCHES > 0 or MOBILE_SEARCHES > 0 or ranDailySets or ranMoreActivities):
            if APPRISE_ALERTS:
                alerts.notify(title=f'{BOT_NAME}: Account Automation Starting\n\n', 
                            body=f'{EMAIL}\nPoints:\t\t{points} \nCash Value:\t\t${round(points/1300, 3)}\nStarting:\t{recordTime}\n\n\n...')
            streaks = checkStreaks(driver, EMAIL)
            ranRewards = True
            
            if (PC_SEARCHES > 0):
                PC_Search_Helper(driver, EMAIL, PASSWORD, PC_SEARCHES)
            else:
                driver.quit()

            if (MOBILE_SEARCHES > 0):
                Mobile_Search_Helper(EMAIL, PASSWORD, MOBILE_SEARCHES)

            driver = getDriver()
            differenceReport = points
            points = getPoints(EMAIL, PASSWORD, driver)
            message = ''
            if AUTO_REDEEM:
                message = redeem(driver, EMAIL)

            differenceReport = points - differenceReport
            if differenceReport > 0:
                print(f'\tTotal points:\t{points}\n\tValue of Points:\t{round(points/1300, 3)}\n\t{EMAIL} has gained a total of {differenceReport} points!\n\tThat is worth ${round(differenceReport/1300, 3)}!\nStreak Status:{streaks}\n\nStart Time:\t{recordTime}\nEnd Time:\t{datetime.datetime.now(TZ)}\n\n\n...')
                report = f'\nPoints:\t\t\t{points}\nCash Value:\t\t${round(points / 1300, 3)}\n\nEarned Points:\t\t\t{differenceReport}\nEarned Cash Value:\t${round(differenceReport/1300,3)}\n{message}\n\nStart Time:\t{recordTime}\nEnd Time:\t{datetime.datetime.now(TZ)}'
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account Automation Completed!:\n', 
                        body=f'{EMAIL}\n{report}\n\n...')
                    
        driver.quit()
        totalPointsReport += points
        totalDifference += differenceReport
        print(f'\tFinished: {datetime.datetime.now(TZ)}\n\n')
    if ranRewards and totalDifference > 0:
        report = f'\nAll accounts for {BOT_NAME} have been automated.\nTotal Points (across all accounts):\t\t{totalPointsReport}\nCash Value of Total Points:\t\t${round(totalPointsReport/1300, 3)}\n\nTotal Earned (in latest run):\t\t{totalDifference}\nCash Value of Earned (in latest run):\t\t${round(totalDifference/1300, 3)}\n\nStart Time: {loopTime}\nEnd Time:{datetime.datetime.now(TZ)}'
        print(report)
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Automation Complete\n', 
                        body=f'{report}\n\n...')
    return

# Main function
def main():
    while True:
        # If timer is set, check if the current time is between the start and end time-- and loop until it is
        if TIMER:
            wait()
        try:
            # Run Bing Rewards Automation
            runRewards()
            hours = random.randint(1, 6)
            print(f'Bing Rewards Automation Complete!\n{datetime.datetime.now(TZ)}\nSleeping for {hours} hours before rechecking...\n\n')
            sleep(3600 * hours)
        except Exception as e:
            # Catch any errors, print them, and restart (in hopes of it being non-fatal)
            print(f'Exception: {e}\n\n{traceback.format_exc()}\n\n\n Attempting to restart Bing Rewards Automation in 10 minutes...')
            if APPRISE_ALERTS:
                alerts.notify(title=f'{BOT_NAME}: Failed!',
                        body=f'EXCEPTION: {e} \n\n{traceback.format_exc()} \nAttempting to restart in 10 minutes...\n\n ')
            sleep(600)
            continue

if __name__ == "__main__":
    # Initialize apprise alerts
    if APPRISE_ALERTS:
        alerts = apprise_init()

    # Run checks on IP address & start main function, if all is good
    check_ip_address()
    main()
