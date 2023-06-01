<h1 align="center">📊 Bing Rewards Automation 🤖 </h1>

<p align="center">An <i>awesome</i> Python script to automate bing searches, quizzes, polls, and more across multiple Bing Reward accounts.</p>

<p align="right"> 
        <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/><img src="https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white"/><img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white"/><a href="https://www.buymeacoffee.com/prem.ium" target="_blank"> <img align="right" src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"/></a>
</p>

## Features

- Multiple Bing Rewards Accounts
- Multi-Threading (Optional)
- PC & Mobile Search Automation
- Bing Quiz, Poll, and Explore Automation
- Quests / Punchcard Automation
- 'More Activities' Automation
- Proxy Support
- Locked Account Handling
- Auto-Redemption
- Apprise Alerts
- Streak Notifications
- Suspended Account Notifications
- USD ($) & EURO (€) Currency Conversions (More coming)
- Semi-International Accommodations/Support
- Incorrect Account Credentials Detection
- Docker Support & DockerQuickstart.bat 
- Headless Option

## Installation
The bot can be run using Python or Docker.

### Python Script
Run locally:
1. Clone this repository, cd into it, and install dependancies:
```sh
   git clone https://github.com/Prem-ium/BingRewards.git
   cd BingRewards
   pip install -r requirements.txt
   ```
2. Rename `.env.example` to `.env` and configure your `.env` file (See below and example for options)
3. Run the script:
```sh
   python main.py
```

### Docker Container
View on [Docker Hub](https://hub.docker.com/repository/docker/nelsondane/bing-rewards)
1. Download and install Docker on your system
2. Configure your `.env` file (See below and example for options)
3. To start the bot using our prebuilt images:
 ```sh
   docker run -it --env-file ./.env --restart unless-stopped --name bing-rewards nelsondane/bing-rewards:<tag>
   ```
   To build the image yourself, cd into the repository and run:
   ```sh
   docker build -t bing-rewards .
   ```
   Then start the bot with:
   ```sh
   docker run -it --env-file ./.env --restart unless-stopped --name bing-rewards bing-rewards
   ```
   Both methods will create a new container called `bing-rewards`. Make sure you have the correct path to your `.env` file you created.

4. Let the bot log in and begin working. DO NOT PRESS `CTRL-c`. This will kill the container and the bot. To exit the logs view, press `CTRL-p` then `CTRL-q`. This will exit the logs view but let the bot keep running.

You can also open `DockerQuickstart.bat` in a text editor, edit the exisitng path in the file with your own of the BingRewards folder directory and run it to quickly stop and start docker container instances. 

## Environment Variables:

To run this project, you will need to add the following environment variables to your `.env` file. Refer to `.env.example` for further clarification.

### Required Variables:

| Variable  | Description                                                                                                                     |
|-----------|---------------------------------------------------------------------------------------------------------------------------------|
| `LOGIN`   | A string of Bing Rewards login information. Email and Password are separated using a colon and accounts are separated using commas. Check `.env.example` for an example. |
| `URL`     | Sign in link obtained through https://bing.com/                                                                                 |

### Optional Variables:

| Variable              | Description                                                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `HANDLE_DRIVER`       | Boolean (True/False) variable based on whether a user wants webdriver to be installed for them. Defaultly set to True.           |
| `BROWSER`             | `chrome`, `edge`, or `firefox` -- Browser you'd like to use the bot with. In experimental mode. `HANDLE_DRIVER` must be set to True to use. Defaults to `chrome`. |
| `HEADLESS`            | True or False -- Whether the program should run headless or not. Defaults to False.                                            |
| `MULTITHREADING`      | 'True' or 'False' -- Whether the program should run multiple threads to run all accounts at once or not. Defaults to False.     |
| `DELAY_SEARCH`        | Integer value of how long the program should wait between making searches.                                                       |
| `APPRISE_ALERTS`      | Notifications and Alerts. See .env example for more details.                                                                    |
| `KEEP_ALIVE`          | True or False -- Whether you wish to use Flask Threading or not.                                                                |
| `AUTO_REDEEM`         | Handle auto redemption of rewards (checks goal). Amazon is chosen as default.                                                   |
| `SHOPPING`            | True or False -- Attempts to complete a new shopping quiz (Experimental).                                                      |
| `GOAL`                | Selecting goal reward, defaults to Amazon.                                                                                      |
| `AUTOMATE_PUNCHCARD`  | True or False -- Whether bot should automate punchcards.                                                                        |
| `SKIP_MOVIES_AND_TV_PUNCHCARD` | True or False -- Whether the bot should skip the punchcard for Movies and TV shows.                                         |
| `CURRENCY`            | Currency Symbol or Name, currently only supported by USD($), EURO(€) and INR(₹). Defaults to USD.                             |
| `BOT_NAME`            | Bot name, helpful for multiple instances of the bot running with proxy.                                                        |
| `TZ`                  | Your desired Time-Zone. Should be formatted from the [IANA TZ Database](https://www.iana.org/time-zones). Defaults to `America/New York`. |
| `TIMER`               | True or False -- Whether you wish for the program to only run between certain time period.                                      |
| `START_TIME`          | 24 hour format hour you would like to start the program, if timer is enabled. Defaults to 4, 4 AM.                              |
| `END_TIME`            | 24 hour format hour you would like to start the program, if timer is enabled. Defaults to 19, 7 PM.                             |
| `POINTS_PER_SEARCH`   | Amount of points per search rewards in your country. Used to calculate the number of searches needed for maximum points. Defaults to 5. |
| `WANTED_IPV4`         | Your desired external IPv4 address. Set this if you want the bot to not run if your IPv4 address is different than this.         |
| `WANTED_IPV6`         | Your desired external IPv6 address. Set this if you want the bot to not run if your IPv6 address is different than this.         |
| `PROXY`               | Configure a HTTP(S) or SOCKS5 proxy through which all of the bot's traffic will go. Should be in a URI format (e.g., https://1.2.3.4:5678). |
| `DEBUGGING`           | True or False -- Whether you wish to log the bot's error and stacktrace. Defaults to False.                                    |
| `DAILY_SETS`          | True or False -- Whether you wish to complete daily sets, this feature is unavailable in a few markets like India. Defaults to True. |

## Donations
I've been working on this project for a few months now, and I'm really happy with how it's turned out. It's also been a helpful tool for users to earn some extra money with Bing Rewards. I'm currently working on adding new features to the script and working on other similar programs to generate passive income. I'm also working on making the script more user-friendly and accessible to a wider audience.

I'm accepting donations through BuyMeCoffee or GitHub Sponsors. Any amount you can donate will be greatly appreciated.

<div style="display: grid; grid-template-columns: 1fr 1fr; justify-content: center; gap: 10px;">
    <b>Buy Me a Coffee:</b>
    <a href="https://www.buymeacoffee.com/prem.ium" target="_blank" style="text-decoration: none;">
            <img src="https://raw.githubusercontent.com/Prem-ium/youtube-analytics-bot/main/output-examples/media/coffee-logo.png" alt="Buy Me A Coffee" style="height: 80px; width: 320px; box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5);">
        </a>
</div>   
<div style="display: grid; grid-template-columns: 1fr 1fr; justify-content: center; gap: 10px;">
    <b>GitHub Sponsors:</b>
        <a href="https://github.com/sponsors/Prem-ium" target="_blank" style="text-decoration: none;">
            <img src="https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA" alt="GitHub Sponsor" style="height: 80px; width: 320px; box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5);">
        </a>
</div>

Your donations will help me to cover the costs of hosting the project, developing new features, and marketing the project to a wider audience.
Thank you for your support!
## Helper(s)
You can use this Selenium IDE script to help create new Microsoft Accounts slightly faster. (Semi-Automation, captcha and email verification manual):
You can find the script in the [Selenium-IDE-Scripts/Bing](https://github.com/Prem-ium/Selenium-IDE-Scripts/tree/master/Bing) directory of my Selenium IDE Project(s) repository.
## Earning Potential:

Conservatively calculating potential points/earnings per month using this bot w/ a lvl 2 account:

PC Searches: (150 * 30) = 4500

Mobile Searches: (100 * 30) = 3000

Edge Bonus: (20*30) = 600

Daily Sets: (30*30) = 900


This adds up to 9000 points, conservatively (not accounting for streak bonuses or more activities which usually net very high, random amount of points), which ends up being a minimum of $6.92/per month per account on level 2. $34.61/ per month with an instance of 5 level 2 reward accounts.

## License & Contributing

This repository is using the [MIT](https://choosealicense.com/licenses/mit/) license.

If you are a developer who wishes to contribute to this repository, please make a pull-request and request a review when ready for a review. [A special thanks to all those who have contributed to this project.](https://github.com/Prem-ium/BingRewards/graphs/contributors)

## Notes:

- This bot uses the new $1.00 = 1300 points conversion rate. Older Bing Reward accounts may have the old conversion rate of $1.00 = 1050 points. As well as €1.00 = 1500 points conversion rate for Euro based Bing Reward accounts.
