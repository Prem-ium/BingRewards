# Bing Rewards Automation
A selenium based python project which auto completes Bing Reward's daily PC and mobile bing searches across multiple accounts. 

## Installation

### - Install the following dependencies using pip3:
```sh
   pip3 install RandomWords
   pip3 install Selenium
   pip3 install apprise
   pip3 install python-dotenv
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
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file. 

`LOGIN` = 'EMAIL:PASSWORD,EMAIL2:PASSWORD2'

`URL` = 'Sign in link obtained through https://bing.com/'

'APPRISE_ALERTS' = see .env example for more details

## Demo

{coming soon}

## Features

- Multiple Bing Rewards Accounts
- PC & Mobile Search Automation
- More Activities/Bonus Automation
- Bing Quiz, Poll, and Explore Automation
- Apprise Alerts

# To-Do:
- Fix incorrect Points being assigned
- Speed up 'more activities' execution
- Selecting correct answers only on 'This or That' Quiz format. (Currently chooses choices at random for streak completion purposes.)
