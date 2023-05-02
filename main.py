# MIT License
# 
# Copyright (c) 2022 Prem-ium
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, random, traceback, requests, datetime

from selenium                                 import webdriver
from selenium.webdriver.common.by             import By
from selenium.webdriver.support.ui            import WebDriverWait
from selenium.webdriver.support               import expected_conditions as EC
from selenium.webdriver.chrome.options        import Options
from selenium.webdriver.common.keys           import Keys
from selenium.common.exceptions               import NoSuchElementException
from time                                     import sleep
from dotenv                                   import load_dotenv


try:
    from random_words                         import RandomWords
except ImportError:
    os.system("pip install RandomWords")
    from random_words                         import RandomWords
   
try:
    from pytz                                 import timezone
except ImportError:
    os.system("pip install pytz")
    from pytz                                 import timezone

# Load ENV
load_dotenv()
# LOGIN EXAMPLE:
# "EMAIL:PASSWORD,EMAIL:PASSWORD"
if not os.environ["LOGIN"]:
    raise Exception("LOGIN not set. Please enter your login information in .env variable 'LOGIN' in the following format: 'EMAIL:PASSWORD,EMAIL2:PASSWORD2,EMAIL3:PASSWORD3'")
else:
    ACCOUNTS = os.environ["LOGIN"].replace(" ", "").split(",")

# Check number of accounts (limit to 6 per IP address to avoid bans)
if (len(ACCOUNTS) > 6):
    raise Exception(f"You can only have 5 accounts per IP address. Using more increases your chances of being banned by Microsoft Rewards. You have {len(ACCOUNTS)} accounts within your LOGIN env variable. Please adjust it to have 5 or less accounts and restart the program.")

# Set login URL
if not os.environ["URL"]:
    raise Exception("URL env variable not set. Please enter a login URL in .env variable 'URL' obtained from the sign in button of https://bing.com/")
else:
    URL = os.environ["URL"]

# Search terms
TERMS = ["define ", "explain ", "example of ", "how to pronounce ", "what is ", "what is the ", "what is the definition of ",
         "what is the example of ", "what is the pronunciation of ", "what is the synonym of ",
         "what is the antonym of ", "what is the hypernym of ", "what is the meronym of ", "photos of ",
         "images of ", "pictures of ", "pictures of ", "pictures of ", "pictures of ", "pictures of ", "pictures of ",
         "information about ", "information on ", "information about the ", "information on the ", "information about the ",
         "synonym of ", "antonym of ", "hypernym of ", "meronym of ", "synonym for ", "antonym for ", "hypernym for "]

# Optional Variables
# Import bot name from .env
BOT_NAME = os.environ.get("BOT_NAME", "Bing Rewards Automation")

# Get browser and whether to use the chromewebdriver or not
BROWSER = os.environ.get("BROWSER", "chrome").lower()
HANDLE_DRIVER = os.environ.get("HANDLE_DRIVER", "True").lower()

# Enable/Disable detailed logging with stacktrace
if (os.environ.get("DEBUGGING", "False").lower() == "true"):
    DEBUGGING = True
else:
    DEBUGGING = False

# Enable/Disable Daily Set
if (os.environ.get("DAILY_SET", "True").lower() == "true"):
    DAILY_SET = True
else:
    DAILY_SET = False


# Import browser libraries
if (HANDLE_DRIVER == "true"):
    HANDLE_DRIVER = True

    if BROWSER == "chrome":
        from webdriver_manager.chrome                                 import ChromeDriverManager
        from selenium.webdriver.chrome.service                        import Service
    elif BROWSER == "edge":
        from webdriver_manager.microsoft                              import EdgeChromiumDriverManager
        from selenium.webdriver.edge.service                          import Service
    elif BROWSER == "firefox":
        from webdriver_manager.firefox                                import GeckoDriverManager
        from selenium.webdriver.firefox.options                       import Options
else:
    HANDLE_DRIVER = False

# Whether to fully automate redemptions
if (os.environ.get("AUTO_REDEEM", "False").lower() == "true"):
    AUTO_REDEEM = True
    GOAL = os.environ.get("GOAL", "amazon.com").lower()
else:
    AUTO_REDEEM = False

# Whether to use keep_alive.py
if (os.environ.get("KEEP_ALIVE", "False").lower() == "true"):
    from keep_alive                                                  import keep_alive
    keep_alive()

# Whether to automate punch-cards.
if (os.environ.get("AUTOMATE_PUNCHCARD", "false").lower() == "true"):
    AUTOMATE_PUNCHCARD = True
else:
    AUTOMATE_PUNCHCARD = False

if (os.environ.get("SHOPPING", "false").lower() == "true"):
    SHOPPING = True
else:
    SHOPPING = False

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

HEADLESS = os.environ.get("HEADLESS", "False").lower()
if (HEADLESS == "true"):
    HEADLESS = True
else:
    HEADLESS = False

MULTITHREADING = os.environ.get("MULTITHREADING", "False").lower()
if (MULTITHREADING == "true"):
    import threading
    MULTITHREADING = True
    print('Multithreading is enabled in .env.\nThis will allow you to run multiple accounts at once, but it may also increase the chance of being banned and leads to more CPU usage.\nUse at your own risk.')
    print('Multithreading is EXPERIMENTAL and may not work properly. If you encounter any issues, please report them to the GitHub repository or try running without it enabled.')
else:
    MULTITHREADING = False

# Get IPs if it's set in .env
WANTED_IPV4 = os.environ.get("WANTED_IPV4")
WANTED_IPV6 = os.environ.get("WANTED_IPV6")
# Get proxy settings from .env
# Note that we should set '' instead of None in case PROXY is not defined to prevent the proxies dict below from being invalid (which breaks our IP checker)
PROXY = os.environ.get("PROXY", "")
# Populate proxy dictionary for requests
PROXIES = {"http": f"{PROXY}", "https": f"{PROXY}"}

# Configure timezone
TZ = timezone(os.environ.get("TZ", "America/New_York"))

# Whether or not to use a timer, and if so, what time to use
TIMER = os.environ.get("TIMER", "False").lower()
if TIMER == "true":
    TIMER = True
    # Get start and end time, defaulting to 4:00am and 7:00pm
    START_TIME = float(os.environ.get("START_TIME", "4"))
    END_TIME = float(os.environ.get("END_TIME", "19"))

    # Make sure start and end times are valid, otherwise switch them
    if START_TIME > END_TIME:
        print("Start time must be before end time, switching times...")
        temp = START_TIME
        START_TIME = END_TIME
        END_TIME = temp
else:
    TIMER = False

CURRENCY = os.environ.get("CURRENCY", "USD").lower()

# More currencies to be added once we get more information on conversion rates across different currencies
if CURRENCY == "usd" or CURRENCY == "$":
    CURRENCY = 1300
    CUR_SYMBOL = "$"
elif CURRENCY == "euro" or CURRENCY == "€":
    CURRENCY = 1500
    CUR_SYMBOL = "€"
elif CURRENCY == "inr" or CURRENCY == "₹":
    CURRENCY = 16
    CUR_SYMBOL = "₹"

if os.environ.get("DELAY_SEARCH"):
    try:
        DELAY_SEARCH = int(os.environ["DELAY_SEARCH"])
    except ValueError:
        print("Invalid value for DELAY_SEARCH, using default of 5 seconds.")
        DELAY_SEARCH = 5
    except:
        print("Unexpected error:", traceback.format_exc())
        DELAY_SEARCH = 5
else:
    DELAY_SEARCH = False
try:
    POINTS_PER_SEARCH = int(os.environ.get("POINTS_PER_SEARCH", "5"))
except ValueError:
    print("Invalid value for POINTS_PER_SEARCH, using default of 5 points.")
    POINTS_PER_SEARCH = 5

# Methods
def apprise_init():
    if APPRISE_ALERTS:
        alerts = apprise.Apprise()
        for service in APPRISE_ALERTS:
            alerts.add(service)
        return alerts
          
def get_current_ip(type, proxies):
    try:
        return ((requests.get(f"https://ip{type}.icanhazip.com", proxies=proxies)).text).strip("\n")
    except requests.ConnectionError:
        print(f"Unable to get IP{type} address")
        if type == "v4":
            # Send message to console and apprise alert if configured
            print(f"Failed to connect to icanhazip.com over {type}. Is there a problem with your network?")
            if APPRISE_ALERTS:
                alerts.notify(title=f"Failed to connect to icanhazip.com over {type}",
                    body=f"Is there a problem with your network?")
            # Wait some time (to prevent Docker containers from constantly restarting)
            sleep(300)
            raise Exception(f"Failed to connect to icanhazip.com over {type}. Is there a problem with your network?")
        if type == "v6":
            # We can just fail softly if this error occurs with v6. Note that a ConnectionError is raised if a v4-only host tries to connect to a v6 site
            # We can make this fail hard once v6 is actually widely available....
            return None
    except Exception as e:
        # Catch all other errors.
        print(f"An exception occurred while trying to get your current IP address: {e}")
        if APPRISE_ALERTS:
            alerts.notify(title=f"An exception occurred while trying to get your current IP address",
                body=f"{e}")
        # Wait some time (to prevent Docker containers from constantly restarting)
        sleep(60)
        raise Exception

def check_ip_address():
    # Compares desired IP address with actual external IP address
    current_ipv4 = get_current_ip("v4", PROXIES)
    print(f"Current IPv4 Address: {current_ipv4}")
    current_ipv6 = get_current_ip("v6", PROXIES)
    if current_ipv6:
        print(f"Current IPv6 Address: {current_ipv6}")
    # If declared in .env, check the IPv4 address
    if WANTED_IPV4:
        if WANTED_IPV4 != current_ipv4:
            print(f"IPv4 addresses do not match. Wanted {WANTED_IPV4} but got {current_ipv4}")
            if APPRISE_ALERTS:
                alerts.notify(title=f'IPv4 Address Mismatch',body=f'Wanted {WANTED_IPV4} but got {current_ipv4}')
            raise Exception(f"IPv4 addresses do not match. Wanted {WANTED_IPV4} but got {current_ipv4}")
        else:
            print("IPv4 addresses match!")
    # If declared in .env, check the IPv6 address
    if WANTED_IPV6 and current_ipv6:
        if WANTED_IPV6 != current_ipv6:
            print(f"IPv6 addresses do not match. Wanted {WANTED_IPV6} but got {current_ipv6}")
            if APPRISE_ALERTS:
                alerts.notify(title=f'IPv6 Address Mismatch', 
                    body=f'Wanted {WANTED_IPV6} but got {current_ipv6}')
            raise Exception(f"IPv6 addresses do not match. Wanted {WANTED_IPV6} but got {current_ipv6}")
        else:
            print("IPv6 addresses match!")
    print()

def get_driver(isMobile = False):
    if BROWSER == "chrome":
        if not HANDLE_DRIVER:
            options = Options()
        else:
            options = webdriver.ChromeOptions()
    elif BROWSER == "edge":
        options = webdriver.EdgeOptions()
    elif BROWSER == "firefox":
        options = webdriver.FirefoxOptions()

    if HEADLESS:
        if BROWSER == "chrome" or BROWSER == "edge":
            options.add_argument("--headless")
        elif BROWSER == "firefox":
            options.headless = True

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")

    if PROXY:
        options.add_argument(f'--proxy-server={PROXY}')
        print(f"Set Browser proxy to {PROXY}")

    if (isMobile):   
        mobile_emulation = {"deviceName": "Nexus 5"}
        options.add_experimental_option("mobileEmulation", mobile_emulation)
    elif BROWSER != "edge":
        # Set to edge user agent if not mobile
        user_agent = "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/64.0.3282.140 safari/537.36 edge/18.17763"
        options.add_argument(f'user-agent={user_agent}')

    if BROWSER == "chrome":
        if not HANDLE_DRIVER:
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(cache_valid_range=30).install()),
                options=options)
    elif BROWSER == "edge":
        driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager(cache_valid_range=30).install()),
            options=options)
    elif BROWSER == "firefox":
        driver = webdriver.Firefox(
            service=Service(GeckoDriverManager(cache_valid_range=30).install()),
            options=options)
    driver.maximize_window()
    return driver

def wait():
    currentHour = datetime.datetime.now(TZ).hour
    if not (currentHour >= START_TIME and currentHour < END_TIME):
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
    try:
        message = driver.find_element(By.XPATH, value='//*[@id="usernameError"]').text
        if("microsoft account doesn't exist" in message.lower()):
            print(f"Microsoft account {EMAIL} doesn't exist. Skipping this account & moving onto the next in env...")
            if APPRISE_ALERTS:
                alerts.notify(title=f'{BOT_NAME} - Account does not exist.', 
                    body=f"Microsoft account {EMAIL} doesn't exist. Please review login env for spelling errors or create the account with {EMAIL} and restart the bot. Skipping this account...")
            return False
    except:
        pass
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
        message = driver.find_element(By.XPATH, value='//*[@id="passwordError"]').text
        if("password is incorrect" in message.lower()):
            print(f"Microsoft account {EMAIL} has incorrect password in LOGIN env. Skipping...")
            if APPRISE_ALERTS:
                alerts.notify(title=f'{BOT_NAME} - {EMAIL} incorrect password.', 
                    body=f"Microsoft account {EMAIL} has an incorrect password message. Please correct your LOGIN in env and restart the bot. Skipping this account & moving onto the next in env...")
            return False
    except:
        pass
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
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account Locked!', 
                        body=f'Your account {EMAIL} has been locked! Sign in and verify your account.\n\n...')
                print(f"uh-oh, your account {EMAIL} has been locked by Microsoft! Sleeping for 15 minutes to allow you to verify your account.\nPlease restart the bot when you've verified.")
                sleep(900)
                return False
        except NoSuchElementException as e:
            pass
        try:
            message = driver.find_element(By.XPATH, value='//*[@id="iPageTitle"]').text
            if message.lower() == "help us protect your account":
                print(f"uh-oh, your account {EMAIL} will need to manually add an alternative email address!\nAttempting to skip in 50 seconds, if possible...")
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account Secuirity Notice!', 
                        body=f'Your account {EMAIL} requires you to add an alternative email address or a phone number!\nPlease sign in and add one to your account.\n\n\nAttempting to skip, if still possible...')
                sleep(50)
                driver.find_element(By.XPATH, value='//*[@id="iNext"]').click()
        except:
            driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
        finally:
            driver.get('https://rewards.microsoft.com/')
        return True

def do_explore(driver):
    try:
        # wait a random amount of time
        sleep(random.uniform(10, 15))
        # click the "continue" button & wait 8 seconds
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        sleep(8)
    except:
        # if the button cannot be found, do nothing
        pass
    finally:
        # refresh the page
        driver.refresh()

def do_poll(driver):
    try:
        # refresh the page
        driver.refresh()
        try:
            # wait a random amount of time
            sleep(random.uniform(3, 5))
            # click the "continue" button
            driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        except:
            # if the button cannot be found, refresh the page and try again
            driver.refresh()
            sleep(random.uniform(2, 7))
            pass

        try:
            # choose a random answer option
            driver.find_element(By.XPATH, value=f'//*[@id="btoption{int(random.uniform(2,10) % 2)}"]/div[2]/div[2]').click()
        except:
            # if the random option cannot be found, choose the first option
            driver.find_element(By.XPATH, value='//*[@id="btoption0"]/div[2]/div[2]').click()

        # wait 8 seconds
        sleep(8)
        print('\tPoll completed!')
    except:
        # if an error occurs, do nothing
        pass
    # wait 3 seconds
    sleep(3)

def do_quiz(driver):
    # Wait a random amount of time
    sleep(random.uniform(7, 14))

    # Try clicking on an element with a specific XPath
    try:
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        sleep(4)
    except:
        pass

    # Refresh the page
    driver.refresh()

    # Try completing the quiz
    try:
        # Get the number of questions in the quiz
        numberOfQuestions = driver.find_element(By.XPATH, value='//*[@id="QuestionPane0"]/div[2]').text.strip().split("of ")[1]
        numberOfQuestions = int(numberOfQuestions[:-1])

        # Loop through each question and select the first option
        for i in range(numberOfQuestions):
            driver.find_element(By.CLASS_NAME, value='wk_OptionClickClass').click()
            sleep(8)

            # Submit the answer
            driver.find_element(By.CLASS_NAME, value='wk_buttons').find_elements(By.XPATH, value='*')[0].send_keys(Keys.ENTER)
            sleep(5)

        # Print a message indicating that the quiz has been completed
        print('\tQuiz completed!')
        return
    except Exception as e:
        pass

    
    if (driver.find_elements(By.XPATH, value='//*[@id="rqStartQuiz"]') or driver.find_elements(By.CLASS_NAME, value='btOptions') or driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span') or driver.find_elements(By.CLASS_NAME, value='rq_button')):
        try:
            # find the start button element
            start_button = driver.find_element(By.XPATH, value='//*[@id="rqStartQuiz"]')

            # wait up to 10 seconds for the start button to be clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(start_button))

            # click the start button
            start_button.click()
        except Exception as e:
            # if an error occurs, try clicking the start button again
            try:
                driver.find_element(By.XPATH, value='//*[@id="rqStartQuiz"]').click()
            except:
                # if the button still cannot be clicked, do nothing
                pass

        try:
            sleep(3)
            # check if the quiz has credits sections
            if driver.find_elements(By.XPATH, value='//*[@id="rqHeaderCredits"]'):
                # get the number of sections in the quiz
                sections = len(driver.find_element(By.XPATH, value='//*[@id="rqHeaderCredits"]').find_elements(By.XPATH, value='*'))
                # Identify if this is a Warp Speed Quiz or not
                is_warpspeed_quiz = len(driver.find_elements(By.XPATH, value='//div[@id="currentQuestionContainer"]/div[@class="textBasedMultiChoice"]/div[@class="rq_button"]')) > 0

                if is_warpspeed_quiz == True:
                    do_warpspeed_quiz(driver, sections)
                else:
                    # loop through each section
                    for i in range(sections):
                        try:
                            # get the number of choices in the current section
                            choices = len(driver.find_element(By.CLASS_NAME, value='rqCredits').find_elements(By.XPATH, value='*'))
                            # loop through each choice
                            for i in range(choices * 2):
                                # wait 5 seconds
                                sleep(5)
                                # get a random answer option
                                option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{random.randint(0, choices - 1)}"]')
                                # click the option
                                option.click()
                                # wait 10 seconds
                                sleep(10)
                                try:
                                    # if the answer was incorrect, choose another option
                                    while driver.find_element(By.XPATH, value='//*[@id="rqAnsStatus"]').text.lower() == 'oops, try again!':
                                        option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{random.randint(0, choices - 1)}"]')
                                        option.click()
                                        sleep(5)
                                except Exception as e:
                                    print(e)
                                    pass
                                # if the quiz is complete, exit the loop
                                if "great job - you just earned" in driver.find_element(By.XPATH, value='//*[@id="quizCompleteContainer"]/div/div[1]').text.lower():
                                    sleep(5)
                                    break
                            print('\tQuiz completed!')
                            return
                        except:
                            pass
                # if the quiz does not have credits sections
                for i in range(sections):
                    try:
                        # get the number of choices in the current section
                        choices = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span').text
                        choices = int(choices[-1]) - int(choices[0])
                    except:
                        choices = len(driver.find_element(By.CLASS_NAME, value='rqCredits').find_elements(By.XPATH, value='*'))
                    try:
                        # loop through each choice
                        for i in range(choices * 2):
                            # wait 5 seconds
                            sleep(5)
                            # get the ith answer option
                            option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{i}"]')
                            # if the option is correct, click it
                            if option.get_attribute('iscorrectoption') == 'True':
                                option.click()
                        print('\tQuiz completed!')
                        return
                    except Exception:
                        continue
            elif (driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]')):
                # get the number of questions in the quiz
                numberOfQuestions = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]').text.strip().split("of ")[1]

                # loop through each question
                for i in range(int(numberOfQuestions)):
                    # click the answer option card
                    driver.find_element(By.CLASS_NAME, value='btOptionCard').click()
                    # wait 13 seconds
                    sleep(13)

                print('\tQuiz completed!')
                return
        except Exception as e:
            if DEBUGGING:
                print(e)
            else:
                print('\tQuiz failed!')
            pass

def do_warpspeed_quiz(driver, sections):
    for i in range(sections):
        try:
            # get the number of choices in the current section
            choices = len(driver.find_elements(By.XPATH, value='//*[contains(@class, "rqOption")]'))
            # loop through each choice
            for j in range(choices):
                # wait 5 seconds
                sleep(5)
                # pick options one by one
                option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{j}"]')
                # click the option
                option.click()
                # wait 10 seconds
                sleep(10)
                # look for incorrect choices; If none were found after click(s), it means we moved on to the next quiz or the quizzes are done
                if len(driver.find_elements(By.CLASS_NAME, value='rqwrongAns')) == 0:
                    break
            print('\tQuiz completed!')
            return
        except Exception as e:
            if DEBUGGING:
                print(e)
            else:
                print('\tQuiz failed!')
            pass

def assume_task(driver, p="false"):
    try:
        # get the parent window handle
        if p.lower() == "false":
            p = driver.window_handles[len(driver.window_handles) - 1]

        # try to complete a quiz
        if do_quiz(driver):
            driver.close()
            driver._switch_to.window(p)
            driver.refresh()
            return True

        # try to complete a poll
        if do_poll(driver):
            driver.close()
            driver._switch_to.window(p)
            driver.refresh()
            return True

        # try to complete an explore task
        if do_explore(driver):
            driver.close()
            driver._switch_to.window(p)
            driver.refresh()
            return True

        # if all tasks fail, close the window and refresh the parent window
        driver.close()
        driver._switch_to.window(p)
        driver.refresh()
        return False
    except:
        pass

def complete_punchcard(driver):
    try:
        # go to the rewards dashboard
        driver.get('https://rewards.microsoft.com/')
        # wait 5 seconds
        sleep(5)

        # get all the clickable quest links on the page
        quests = driver.find_elements(By.CLASS_NAME, value='clickable-link')
        # create a list of the links
        links = []
        for quest in quests:
            links.append(quest.get_attribute('href'))

        # loop through each link
        for link in links:
            # go to the link
            driver.get(link)
            # wait a random amount of time
            sleep(random.uniform(1, 3))

            try:
                # get the punchcard details
                message = driver.find_element(By.XPATH, '//*[@id="rewards-dashboard-punchcard-details"]/div[2]/div[2]/div[4]').text
                message2 = driver.find_element(By.XPATH, '//*[@id="rewards-dashboard-punchcard-details"]/div[2]/div[2]/div[2]').text

                # if the card has already been completed, skip it
                if message.lower() == 'congratulations!' or "rent" in message2.lower() or "buy" in message2.lower():
                    continue

                # store the current window handle
                p = driver.current_window_handle

                # wait a random amount of time
                sleep(random.uniform(1, 3))

                # try to click the "complete" button
                try:
                    driver.find_element(By.XPATH, value='//*[@id="rewards-dashboard-punchcard-details"]/div[2]/div[2]/div[7]/div[3]/div[1]/a/b').click()
                except:
                    # if the "complete" button cannot be found, click the first offer
                    sleep(5)
                    offers = driver.find_elements(By.CLASS_NAME, value = 'offer-cta')
                    offers[0].find_element(By.CLASS_NAME, value = 'btn').click()

                # get the window handles of all open windows
                chwd = driver.window_handles
                # switch to the new window
                if (chwd[1]):
                    driver._switch_to.window(chwd[1])

                # try to complete the task in the new window
                try:
                    assume_task(driver, p)
                except: 
                    pass
                finally:
                    # wait a random amount of time
                    sleep(random.uniform(3, 5))
            except Exception as e:
                print(traceback.format_exc())
                pass
    except:
        pass

def more_activities(driver):
    ran = False

    # Go to rewards page
    driver.get('https://rewards.microsoft.com/')

    try:
        # Get the number of activity cards on the page
        count = len(driver.find_elements(By.CLASS_NAME, 'ds-card-sec')) - 6

        for i in range(count):
            i += 1
            try:
                # Get the element for the current activity card
                element = driver.find_element(By.XPATH, value=f'/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-more-activities-card/mee-card-group/div/mee-card[{i}]')

                # Get the class name for the element that indicates whether the activity is available or not
                class_name = element.find_element(By.XPATH, value=f'/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-more-activities-card/mee-card-group/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a/mee-rewards-points/div/div/span[1]').get_attribute('class')

                # Check if the activity is available
                if (class_name == "mee-icon mee-icon-AddMedium" or class_name == "mee-icon mee-icon-HourGlass"):
                    # Click on the activity to open it in a new window
                    assign = driver.find_element(By.XPATH, value=f'//*[@id="more-activities"]/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a')
                    p = driver.current_window_handle
                    assign.click()

                    # Click on the "I agree" button, if it is present
                    try:
                        driver.find_element(By.XPATH, value='//*[@id="legalTextBox"]/div/div/div[3]/a').click()
                    except:
                        pass

                    # Switch to the new window and perform the activity
                    chwd = driver.window_handles
                    if (chwd[1]):
                        driver._switch_to.window(chwd[1])
                        try:
                            ran = assume_task(driver, p)
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

def daily_set(driver):
    ranSets = False

    # Check if the first activity is available
    try:
        if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
            # Open the activity in a new window
            p = driver.current_window_handle
            driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
            chwd = driver.window_handles
            driver._switch_to.window(chwd[1])

            # Perform the activity
            do_explore(driver)

            # Close the window and refresh the page
            driver.close()
            driver._switch_to.window(p)
            driver.refresh()
            ranSets = True
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        if DEBUGGING:
            print(e)
        else:
            print("Error: Could not complete daily set activity 1")
        pass

    # Check if the second activity is available
    try:
        if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
            # Open the activity in a new window
            p = driver.current_window_handle
            driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
            chwd = driver.window_handles
            driver._switch_to.window(chwd[1])

            # Perform the activity
            do_poll(driver)

            # Close the window and refresh the page
            driver.close()
            driver._switch_to.window(p)
            driver.refresh()
            ranSets = True
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        if (DEBUGGING):
            print(e)
        else:
            print("Error: Could not complete daily set activity 2")
        pass
    # Check if the third activity is available
    try:
        if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium" or driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") =="mee-icon mee-icon-HourGlass"):
            # Open the activity in a new window
            p = driver.current_window_handle
            driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
            chwd = driver.window_handles
            driver._switch_to.window(chwd[1])

            # Perform the activity
            do_quiz(driver)

            # Close the window and refresh the page
            driver.close()
            driver._switch_to.window(p)
            driver.refresh()
            ranSets = True
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        if (DEBUGGING):
            print(e)
        else:
            print("Error: Could not complete daily set activity 3")
        pass

    return ranSets

def retrieve_streaks(driver, EMAIL):
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

def redeem(driver, EMAIL):
    # Navigate to rewards page
    driver.get("https://rewards.microsoft.com/")
    
    try:
        # Check if a goal needs to be set
        element = driver.find_element(By.XPATH, value = '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/div/a/span/ng-transclude')
        setG = element.text
        if ("set goal" in setG.lower()):
            element.click()
            sleep(3)
            elements = driver.find_elements(By.CLASS_NAME,"c-image")
            for e in elements:
                if (GOAL in e.get_attribute("alt").lower()):
                    print(f'\tGoal set as {GOAL}!')
                    e.click()
                    break
    except:
        pass
    finally:
        driver.get("https://rewards.microsoft.com/")
    
    try:
        # Check if points are ready to be redeemed
        position = driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/p').text.replace(" ", "").split("/")
        points = int(position[0].replace(",", ""))
        total = int(position[1].replace(",", ""))

        goal = driver.find_element(By.XPATH, value = '//*[@id="dashboard-set-goal"]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/h3').text
        print(f'\t{goal}')

        if (points < total):
            print(f"\t{total - points} points left to redeem your goal!")
            return f'\nPoints Remaining until {goal} Redeemption:\t{total - points} ({CUR_SYMBOL}{round((total - points) / CURRENCY, 3)})\n'
        elif(points >= total):
            print("\tPoints are ready to be redeemed!\n\tIf this is the first time, manual SMS verification is required.")
    except Exception as e:
        print(traceback.format_exc())
        return f"Ran into an exception trying to redeem\n{traceback.format_exc()}\n"
    # Try to click on the redeem button
    try:
        driver.find_element(By.XPATH, value = '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/div/a[1]/span/ng-transclude').click()
        sleep(random.uniform(2, 4))
    except:
        sleep(random.uniform(3, 5))
        driver.find_element(By.XPATH, value = '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-redeem-info-card/div/mee-card-group/div/div[1]/mee-card/div/card-content/mee-rewards-redeem-goal-card/div/div[2]/div/a[1]').click()

    # Try to redeem the rewards
    try:
        # Get the id of the rewards
        url = driver.current_url
        url = url.split('https://rewards.microsoft.com/redeem/')
        id = url[1]
        try:
            # Click on the rewards
            driver.find_element(By.XPATH, value = f'//*[@id="redeem-pdp_{id}"]').click()
            sleep(random.uniform(3, 5))
        except:
            driver.find_element(By.XPATH, value = f'//*[@id="redeem-pdp_{id}"]/span[1]').click()

        # Confirm the rewards redemption
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
        sleep(random.uniform(10, 20))
        try:
            error = driver.find_element(By.XPATH, value = '//*[@id="productCheckoutError"]/div/div[1]').text
            if ("issue with your account or order" in message.lower()):
                message = f'{EMAIL} has encountered the following message while attempting to auto-redeem rewards:\n{error}\nUnfortunately, this is likely means this account has been shadow-banned. You may test your luck and contact support or just close the account to try again on another account.\n\n...'
                print(message)
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account/Order Issue', body=message)
                return message
        except:
            pass

        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Rewards Redeemed!', body=f'{EMAIL} has successfully redeemed rewards!\n\n...')
        print('\tRewards redeemed successfully!')
        return f"{EMAIL} has successfully redeemed rewards!"

    except Exception as e:
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Redeem Error', body=f'An error occured trying to auto-redeem for: {EMAIL}\n\n{traceback.format_exc()}\n\n...')
        if DEBUGGING:
            print(e)
        else:
            print("Ran into an exception trying to redeem\n")
        return f"\tRan into an exception trying to redeem\n{traceback.format_exc()}\n"

def get_points(EMAIL, PASSWORD, driver):
    # Set initial value for points
    points = -1

    # Wait for the page to load
    driver.implicitly_wait(5)
    sleep(random.uniform(3, 5))

    try:
        # Go to the sign-in page
        driver.get('https://rewards.microsoft.com/Signin?idru=%2F')

        # Attempt to login
        if not login(EMAIL, PASSWORD, driver):
            return -404

        # If it's the first sign in, join Microsoft Rewards
        if driver.current_url == 'https://rewards.microsoft.com/welcome':
            try:
                join_rewards = driver.find_element(By.XPATH, value='//*[@id="start-earning-rewards-link"]')
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(join_rewards)
                )
                join_rewards.click()
                print(f'Joined Microsoft Rewards on account {EMAIL}')
            except:
                try:
                    driver.find_element(By.XPATH, value='//*[@id="start-earning-rewards-link"]').click()
                    print(f'Joined Microsoft Rewards on account {EMAIL}')
                except:
                    print(traceback.format_exc())
                    print("Got Rewards welcome page, but couldn't join Rewards.")
                    return -404

            # Check if the user has completed the welcome tour
            try:
                if driver.current_url == 'https://rewards.microsoft.com/welcometour':
                    driver.find_element(By.XPATH, value='//*[@id="welcome-tour"]/mee-rewards-slide/div/section/section/div/a[2]').click()
            except:
                driver.get('https://rewards.microsoft.com/')

        # Check if the user's account has been suspended
        if driver.title.lower() == 'rewards error':
            try:
                if "microsoft Rewards account has been suspended" in driver.find_element(By.XPATH, value='//*[@id="error"]/h1').text.lower() or "suspended" in driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/main/div/h1').text.lower():
                    print(f"\t{EMAIL} account has been suspended.")

                    if APPRISE_ALERTS:
                        alerts.notify(title=f'{BOT_NAME}: Account Suspended', body=f'Unfortunately, {EMAIL}\'s Bing Rewards account has been suspended. Please remove login details from the bot.\n\n...')
                    return -404
            except:
                sleep(random.uniform(2, 4))
                driver.get('https://rewards.microsoft.com/')
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        if DEBUGGING:
            print(e)
        else:
            print("Ran into an exception trying to login and getting your points\n")
        pass
    finally:
        sleep(random.uniform(8, 20))

    xpaths = [
        '//*[@id="balanceToolTipDiv"]/p/mee-rewards-counter-animation/span',
        '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/mee-rewards-user-status-banner/div/div/div/div/div[2]/div[1]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-balance/div/div/div/div/div/div/p/mee-rewards-counter-animation/span',
        '//*[@id="rewardsBanner"]/div/div/div[2]/div[1]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-balance/div/div/div/div/div/p/mee-rewards-counter-animation/span',
        '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/mee-rewards-user-status-banner/div/div/div/div/div[2]/div[1]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-balance/div/div/div/div/div/p/mee-rewards-counter-animation/span',
        '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span',
        '//*[@id="rewardsBanner"]/div/div/div[2]/div[2]/span',
    ]

    for xpath in xpaths:
        try:
            element = driver.find_element(By.XPATH, xpath)
            points = element.text.strip().replace(',', '')
            return int(points)
        except:
            pass
    return -1


def pc_search(driver, EMAIL, PASSWORD, PC_SEARCHES):
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
        if DELAY_SEARCH:
            sleep(DELAY_SEARCH)
        else:
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

def pc_search_helper(driver, EMAIL, PASSWORD, PC_SEARCHES):
    try:
        # Perform the PC search
        pc_search(driver, EMAIL, PASSWORD, PC_SEARCHES)
    except Exception as e:
        # Print the traceback and sleep for 500 seconds
        print('PC Search failed.')
        if(DEBUGGING):
            print(traceback.format_exc())
            print('Attempting to restart PC search in 500 seconds')
            sleep(500)
        else:
            print('Attempting to restart PC search in 60 seconds')
            sleep(60)
            
        driver.quit()
        
        # Get the driver again and update the searches
        driver = get_driver()
        try:
            PC_SEARCHES, MOBILE_SEARCHES = update_searches(driver)
            
            # Perform the PC search again
            pc_search(driver, EMAIL, PASSWORD, PC_SEARCHES)
        except Exception as e:
            print('PC search failed, again! Skipping PC search.')
    finally:
        # Quit the driver
        driver.quit()


def mobile_search(driver, EMAIL, PASSWORD, MOBILE_SEARCHES):
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
    # Attempt (MOBILE_SEARCHES+1) searches to make sure the mobile_search finishes completely
    for x in range(1, MOBILE_SEARCHES + 2):
        if DELAY_SEARCH:
            sleep(DELAY_SEARCH)
        else:
            sleep(random.uniform(1, 6))
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

def mobile_helper(EMAIL, PASSWORD, MOBILE_SEARCHES):
    # Get the driver with mobile emulation enabled
    driver = get_driver(True)
    try:
        # Perform the mobile search
        mobile_search(driver, EMAIL, PASSWORD, MOBILE_SEARCHES)
    except Exception as e:
        # Print the traceback and sleep for 500 seconds
        print(traceback.format_exc())
        print('Attempting to restart Mobile search in 500 seconds')
        sleep(500)
        driver.quit()
        
        # Get the driver again and update the searches
        driver = get_driver()
        PC_SEARCHES, MOBILE_SEARCHES = update_searches(driver)
        driver.quit()
        
        # Get the driver with mobile emulation enabled and perform the search again
        driver = get_driver(True)
        try:
            mobile_search(driver, EMAIL, PASSWORD, MOBILE_SEARCHES)
        except Exception as e:
            pass
    finally:
        # Quit the driver
        driver.quit()

  
def update_searches(driver):
    driver.get('https://rewards.microsoft.com/pointsbreakdown')

    PC_SEARCHES = 34
    MOBILE_SEARCHES = 24
    try:
        sleep(10)
        PC = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
        
        if (int(PC[0]) < int(PC[1])):
            PC_SEARCHES = int((int(PC[1]) - int(PC[0])) / POINTS_PER_SEARCH)
            print(f'\tPC Searches Left:\t{PC_SEARCHES}')
        else:
            PC_SEARCHES = 0
            print(f'\tPC Searches Completed:\t{PC[0]}/{PC[1]}')

        if (int(PC[1]) > 50):
            MOBILE = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            if (int(MOBILE[0]) < int(MOBILE[1])):
                MOBILE_SEARCHES = int((int(MOBILE[1]) - int(MOBILE[0])) / POINTS_PER_SEARCH)
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
        print("Error fetching points breakdown.")
        if(DEBUGGING):
            print(traceback.format_exc())
        
        pass
    finally:
        print()
        return PC_SEARCHES, MOBILE_SEARCHES

def shopping_attempt(driver):
    try:
        driver.get('https://www.msn.com/en-us/shopping')
        driver.execute_script('var msnShoppingGamePane = document.querySelector("shopping-page-base") ?.shadowRoot.querySelector("shopping-homepage") ?.shadowRoot.querySelector("msft-feed-layout")?.shadowRoot.querySelector("msn-shopping-game-pane");if(msnShoppingGamePane != null){msnShoppingGamePane.cardsPerGame = 1;msnShoppingGamePane.resetGame();}')
    except:
        pass
def multi_method(EMAIL, PASSWORD):
    driver = get_driver()
    PC_SEARCHES = 34
    MOBILE_SEARCHES = 20

    # Retireve points before completing searches
    points = get_points(EMAIL, PASSWORD, driver)
    if (points == -404):
        driver.quit()
        return
    print(f'Email:\t{EMAIL}\n\tPoints:\t{points:,}\n\tCash Value:\t{CUR_SYMBOL}{round(points/CURRENCY,3)}\n')
    PC_SEARCHES, MOBILE_SEARCHES = update_searches(driver)
    
    recordTime = datetime.datetime.now(TZ)
    
    if AUTOMATE_PUNCHCARD:
        complete_punchcard(driver)

    if AUTO_REDEEM:
        redeem(driver, EMAIL)
    ranMore = more_activities(driver)
    ranSet = False
    if DAILY_SET:
        ranSet = daily_set(driver)

    if (PC_SEARCHES > 0 or MOBILE_SEARCHES > 0 or ranSet or ranMore):
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Account Automation Starting\n\n', 
                        body=f'Email:\t\t{EMAIL}\nPoints:\t\t{points:,} ({CUR_SYMBOL}{round(points/CURRENCY, 3):,})\nStarting:\t{recordTime}\n...')
        streaks = retrieve_streaks(driver, EMAIL)
        ranRewards = True
        
        if (PC_SEARCHES > 0):
            pc_search_helper(driver, EMAIL, PASSWORD, PC_SEARCHES)
        else:
            print(f'\tPC Searches Left:\t{PC_SEARCHES}')
            driver.quit()

        if (MOBILE_SEARCHES > 0):
            print(f'\tMobile Searches Left:\t{MOBILE_SEARCHES}')
            mobile_helper(EMAIL, PASSWORD, MOBILE_SEARCHES)
        else:
            print(MOBILE_SEARCHES, MOBILE_SEARCHES > 0)
        driver = get_driver()
        differenceReport = points
        points = get_points(EMAIL, PASSWORD, driver)
        message = ''
        if SHOPPING:
            shopping_attempt(driver)
        if AUTO_REDEEM:
            message = redeem(driver, EMAIL)
        
        differenceReport = points - differenceReport
        if differenceReport > 0:
            print(f'\tTotal points:\t{points:,}\n\tValue of Points:\t{round(points/CURRENCY, 3):,}\n\t{EMAIL} has gained a total of {differenceReport:,} points!\n\tThat is worth {CUR_SYMBOL}{round(differenceReport/CURRENCY, 3):,}!\nStreak Status:{streaks}\n\nStart Time:\t{recordTime}\nEnd Time:\t{datetime.datetime.now(TZ)}\n\n\n...')
            report = f'Points:\t\t\t{points:,} ({CUR_SYMBOL}{round(points / CURRENCY, 3):,})\nEarned Points:\t\t\t{differenceReport:,} ({CUR_SYMBOL}{round(differenceReport/CURRENCY,3):,})\n{message}\nStart Time:\t{recordTime}\nEnd Time:\t{datetime.datetime.now(TZ)}'
            if APPRISE_ALERTS:
                alerts.notify(title=f'{BOT_NAME}: Account Automation Completed!:\n', 
                    body=f'Email:\t{EMAIL}\n{report}\n\n...')
                
    driver.quit()
    totalPointsReport += points
    totalDifference += differenceReport
    print(f'\tFinished {EMAIL}: {datetime.datetime.now(TZ)}\n\n')

def start_rewards():
    totalPointsReport = totalDifference = differenceReport = 0
    ranRewards = False
    loopTime = datetime.datetime.now(TZ)
    print(f'\nStarting Bing Rewards Automation:\t{loopTime}\n')
    for x in ACCOUNTS:
        driver = get_driver()

        # Grab email
        colonIndex = x.index(":")+1
        EMAIL = x[0:colonIndex-1]
        PASSWORD = x[colonIndex:len(x)]

        # Set default search amount
        PC_SEARCHES = 34
        MOBILE_SEARCHES = 20
        try:
            # Retireve points before completing searches
            points = get_points(EMAIL, PASSWORD, driver)
        except:
            driver.quit()
            driver = get_driver()
            try:
                points = get_points(EMAIL, PASSWORD, driver)
            except:
                driver.quit()
                continue
        if (points == -404):
            driver.quit()
            continue
        print(f'Email:\t{EMAIL}\n\tPoints:\t{points}\n\tCash Value:\t{CUR_SYMBOL}{round(points/CURRENCY,3)}\n')
        try:
            PC_SEARCHES, MOBILE_SEARCHES = update_searches(driver)
            
            recordTime = datetime.datetime.now(TZ)
            ranDailySets = daily_set(driver)
            ranMoreActivities = more_activities(driver)
            if AUTOMATE_PUNCHCARD:
                complete_punchcard(driver)
    
            if AUTO_REDEEM:
                redeem(driver, EMAIL)
        except:
            print(traceback.format_exc())
            driver.quit()
            driver = get_driver()

        if (PC_SEARCHES > 0 or MOBILE_SEARCHES > 0 or ranDailySets or ranMoreActivities):
            if APPRISE_ALERTS:
                alerts.notify(title=f'{BOT_NAME}: Account Automation Starting\n\n', 
                            body=f'Email:\t\t{EMAIL}\nPoints:\t\t{points:,} ({CUR_SYMBOL}{round(points/CURRENCY, 3):,})\nStarting:\t{recordTime}\n...')
            try:
                streaks = retrieve_streaks(driver, EMAIL)
                ranRewards = True
                
                if (PC_SEARCHES > 0):
                    pc_search_helper(driver, EMAIL, PASSWORD, PC_SEARCHES)
            except:
                print(traceback.format_exc())
            finally:
                driver.quit()
            try:
                if (MOBILE_SEARCHES > 0):
                    mobile_helper(EMAIL, PASSWORD, MOBILE_SEARCHES)

                driver = get_driver()
                differenceReport = points
                points = get_points(EMAIL, PASSWORD, driver)
                message = ''
                if SHOPPING:
                    shopping_attempt(driver)
                if AUTO_REDEEM:
                    message = redeem(driver, EMAIL)
            except:
                print(traceback.format_exc())
            finally:
                driver.quit()


            differenceReport = points - differenceReport
            if differenceReport > 0:
                print(f'\tTotal points:\t{points:,}\n\tValue of Points:\t{round(points/CURRENCY, 3):,}\n\t{EMAIL} has gained a total of {differenceReport:,} points!\n\tThat is worth {CUR_SYMBOL}{round(differenceReport/CURRENCY, 3):,}!\nStreak Status:{streaks}\n\nStart Time:\t{recordTime}\nEnd Time:\t{datetime.datetime.now(TZ)}\n\n\n...')
                report = f'Points:\t\t\t{points:,} ({CUR_SYMBOL}{round(points / CURRENCY, 3):,})\nEarned Points:\t\t\t{differenceReport:,} ({CUR_SYMBOL}{round(differenceReport/CURRENCY,3):,})\n{message}\nStart Time:\t{recordTime}\nEnd Time:\t{datetime.datetime.now(TZ)}'
                if APPRISE_ALERTS:
                    alerts.notify(title=f'{BOT_NAME}: Account Automation Completed!:\n', 
                        body=f'Email:\t{EMAIL}\n{report}\n\n...')
        try:        
            driver.quit()
        except:
            print(traceback.format_exc())
        totalPointsReport += points
        totalDifference += differenceReport
        print(f'\tFinished: {datetime.datetime.now(TZ)}\n\n')
    if ranRewards and totalDifference > 0:
        report = f'\nAll accounts for {BOT_NAME} have been automated.\nTotal Points (across all accounts):\t\t{totalPointsReport:,} ({CUR_SYMBOL}{round(totalPointsReport/CURRENCY, 3):,})\n\nTotal Earned (in latest run):\t\t{totalDifference} ({CUR_SYMBOL}{round(totalDifference/CURRENCY, 3):,})\n\nStart Time: {loopTime}\nEnd Time:{datetime.datetime.now(TZ)}'
        print(report)
        if APPRISE_ALERTS:
            alerts.notify(title=f'{BOT_NAME}: Automation Complete\n', 
                        body=f'{report}\n\n...')
    return

# Multi-Threading Function
def multi_threading():
    # Multithreading. 1 thread per account, run all accounts at the same time on different threads
        threads = []
        for x in ACCOUNTS:
            colonIndex = x.index(":")+1
            EMAIL = x[0:colonIndex-1]
            PASSWORD = x[colonIndex:len(x)]
            t = threading.Thread(target=multi_method, args=(EMAIL, PASSWORD))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()

# Main function
def main():
    while True:
        # If timer is set, check if the current time is between the start and end time-- and loop until it is
        if TIMER:
            wait()
        try:
            if MULTITHREADING:
                multi_threading()
            else:
                # Run Bing Rewards Automation
                start_rewards()
            hours = random.randint(3, 8)
            print(f'Bing Rewards Automation Complete!\n{datetime.datetime.now(TZ)}\n\n------------------------------------------------------------\n\nIf you like this project, please consider showing support to the developer!\nGitHub Profile:\t\t\t\thttps://github.com/Prem-ium\nBuy-Me-A-Coffee Donations:\thttps://www.buymeacoffee.com/prem.ium\n\n------------------------------------------------------------\n\nSleeping for {hours} hours before restarting Bing Rewards Automation.\nThank you for supporting Prem-ium\'s Github Repository!\n\n------------------------------------------------------------\n')
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
