# Bing Rewards Automation
A selenium based python project which auto completes Bing Reward's daily PC and mobile bing searches across multiple accounts. 

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file. 

`LOGIN` = A string of Bing Rewards login information. Email and Password are seperated using a colon and accounts are seperated using commas. Check .env.example file for an example.

`URL` = Sign in link obtained through https://bing.com/

Optional Variables:

`HANDLE_DRIVER` = Boolean (True/False) variable based on whether a user wants webdriver to be installed for them. Defaultly set to False.

`APPRISE_ALERTS` = see .env example for more details

`WANTED_IPV4` = Your desired external IPV4 address. Set this if you want the bot to not run if your IPv4 address is different than this.

`WANTED_IPV6` = Your desired external IPv6 address. Set this if you want the bot to not run if your IPv6 address is different than this.

`PROXY` = # Configure a HTTP(S) or SOCKS5 proxy through which all of the bot's traffic will go. Should be in a URI format (e.g., https://1.2.3.4:5678)

## Installation

### - Install the following dependencies using pip3:
```sh
   pip3 install RandomWords
   pip3 install Selenium
   pip3 install apprise
   pip3 install python-dotenv
   pip3 install pytz
   ```
Alternatively, you can clone this repository and install using requirements.txt
```sh
   git clone https://github.com/sazncode/Bing-Rewards.git
   cd Bing-Rewards
   pip3 install -r requirements.txt
   ```
### - Start the program
```sh
   python main.py
```

### Docker Container
View on [Docker Hub](https://hub.docker.com/repository/docker/nelsondane/bing-rewards)
1. Download and install Docker on your system
2. Run: `docker run -it --env-file ./.env --restart unless-stopped --name bing-rewards nelsondane/bing-rewards:<tag>`. This creates a new container called bing-rewards. Make sure you have the correct path to your `.env` file you created.

Let the bot log in, this could take a minute. Make sure the bot logs in correctly: wait until it prints your email and points. DO NOT PRESS CTRL-C. This will kill the container. To exit the logs view, press CTRL-p then CTRL-q. This will exit the logs view but let the bot keep running.

### Available Docker Tags
Replace the `<tag>` above with one of these (defaults to `latest`)
- `latest`: latest stable release on [Sazn's GitHub](https://github.com/sazncode/Bing-Rewards)
- `beta`: latest beta release on [NelsonDane's GitHub](https://github.com/NelsonDane/Bing-Rewards)

## Demo

{coming soon}

## Features

- Multiple Bing Rewards Accounts
- PC & Mobile Search Automation
- More Activities/Bonus Automation
- Bing Quiz, Poll, and Explore Automation
- Apprise Alerts

## To-Do:
- Selecting only correct answers on 'This or That' Quiz format. (Currently chooses choices at random for streak completion purposes.)
