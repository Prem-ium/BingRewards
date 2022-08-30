# Bing Rewards Automation
An awesome python script to automate bing searches, quizes, polls, and more across multiple Bing Reward accounts.

## Features

- Multiple Bing Rewards Accounts
- PC & Mobile Search Automation
- Bing Quiz, Poll, and Explore Automation
- 'More Activities' Automation
- Locked Account Handling
- Apprise Alerts
- Streak Notifications

## Installation
The bot can be run using Python or Docker.
### Python Script
1. Clone this repository, cd into it, and install dependancies:
```sh
   git clone https://github.com/sazncode/BingRewards.git
   cd Bing-Rewards
   pip install -r requirements.txt
   ```
2. Configure your `.env` file (See below and example for options)
3. Run the script:
```sh
   python main.py
```

### Docker Container
View on [Docker Hub](https://hub.docker.com/repository/docker/nelsondane/bing-rewards)
1. Download and install Docker on your system
2. Configure your `.env` file (See below and example for options)
3. Start the bot using Docker Run:
 ```sh
   docker run -it --env-file ./.env --restart unless-stopped --name bing-rewards nelsondane/bing-rewards:<tag>
   ```
   This creates a new container called bing-rewards. Make sure you have the correct path to your `.env` file you created.

4. Let the bot log in and begin working. DO NOT PRESS CTRL-c. This will kill the container and the bot. To exit the logs view, press CTRL-p then CTRL-q. This will exit the logs view but let the bot keep running.

### Available Docker Tags
Replace the `<tag>` above with one of these (defaults to `latest`)
- `latest`: latest stable release on [Sazn's GitHub](https://github.com/sazncode/Bing-Rewards)
- `beta`: latest beta release on [NelsonDane's GitHub](https://github.com/NelsonDane/Bing-Rewards)

## Environment Variables:

To run this project, you will need to add the following environment variables to your `.env` file. 

`LOGIN` = A string of Bing Rewards login information. Email and Password are seperated using a colon and accounts are seperated using commas. Check `.env.example` for how an example.

`URL` = Sign in link obtained through https://bing.com/

### Optional .env Variables:

`HANDLE_DRIVER` = Boolean (True/False) variable based on whether a user wants webdriver to be installed for them. Defaultly set to False.

`APPRISE_ALERTS` = Notifications and Alerts. See .env example for more details

`WANTED_IPV4` = Your desired external IPV4 address. Set this if you want the bot to not run if your IPv4 address is different than this.

`WANTED_IPV6` = Your desired external IPv6 address. Set this if you want the bot to not run if your IPv6 address is different than this.

`PROXY` = Configure a HTTP(S) or SOCKS5 proxy through which all of the bot's traffic will go. Should be in a URI format (e.g., https://1.2.3.4:5678)

`TZ` = Your desired Time-Zone. Defaults to America/New York

`TIMER` = True or False. Whether you wish for the program to only run between certain time period.

`START_TIME` = 24 hour format hour you would like to start the program, if timer is enabled. Defaults to 4, 4 AM

`END_TIME` = 24 hour format hour you would like to start the program, if timer is enabled. Defaults to 23, 11 PM