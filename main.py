from tabnanny import check
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import time
from pprint import pprint
import requests
import captcha
import random
import os

HUNT_CMD="rpg hunt h"
ADV_CMD="rpg adv h"
WORK_CMD="rpg chop"
FARM_CMD="rpg farm"
DATA_DIR="C:/Users/PC/AppData/Local/Google/Chrome/User Data"
PROFILE_DIR="Default"
DISCORD_CHANNEL="https://discord.com/channels/392631512673157120/1177872440332910732"


def sendText(driver: webdriver, text):
    inputArea = driver.find_element(by=By.CSS_SELECTOR, value="div[class^=textArea]")
    innerInputArea = driver.find_element(by=By.CSS_SELECTOR, value="div[class^=textArea] div div[role^=textbox]")
    inputArea.click()
    innerInputArea.send_keys(text)
    innerInputArea.send_keys(Keys.RETURN)

def checkMessages(driver, text):
    messages = driver.find_elements(by=By.CSS_SELECTOR, value="div[id^=message-content]")
    if len(messages) >= 10:
        lastMessages = messages[-10:]
        for msg in lastMessages:
            if text in msg.text:
                return True
    return False

def isInJail(driver):
    return checkMessages(driver, "jail")

def backToWork(driver):
    return checkMessages(driver, "I solemnly swear that I am up to no good")

def killBot(driver):
    return checkMessages(driver, "Mischief managed")

# def shouldBeHealing(driver):
    # if checkMessages(driver, "Start healing"):
    #     return True
    # elif checkMessages(driver, "Stop healing"):
    #     return False
    # return None

def changeWorkCommand(driver):
    messages = driver.find_elements(by=By.CSS_SELECTOR, value="div[id^=message-content]")
    if len(messages) >= 10:
        lastMessages = messages[-10:]
        for msg in lastMessages:
            if "chwrk " in msg.text:
                return msg.text[6:]
    return None

def checkCaptcha(driver):
    clear_screen()
    messages = driver.find_elements(by=By.CSS_SELECTOR, value="div[class^=message]")
    if len(messages) >= 5:
        lastMessages = messages[-5:]
        for msg in lastMessages:
            try:
                content = msg.find_element(by=By.CSS_SELECTOR, value="div[id^=message-content]")
                if "We have to check" in content.text:
                    image = msg.find_element(by=By.CSS_SELECTOR, value="div[class^=imageWrapper] a")
                    try:
                        resImg = requests.get(image.get_attribute("href"))
                        with open("captcha.png", "wb") as f:
                            f.write(resImg.content)
                        return True
                    except Exception as e:
                        print(e)
            except Exception as e:
                pass
    return False

def checkArea(driver):
    clear_screen()
    messages = driver.find_elements(by=By.CSS_SELECTOR, value="div[class^=message]")
    if len(messages) >= 5:
        lastMessages = messages[-5:]  # Check the last 5 messages
        for msg in lastMessages:
            try:
                # Locate the content of the message
                content = msg.find_element(by=By.CSS_SELECTOR, value="div[id^=message-content]")
                # Check if "area:" is in the message text
                if "area:" in content.text:
                    # Extract the number after "area:"
                    import re
                    match = re.search(r"area:\s*(\d+)", content.text)
                    if match:
                        area_number = int(match.group(1))  # Convert the matched number to an integer
                        print(f"Found area: {area_number}")

                        confirm = input('\nconfirm?\t')
                        if confirm.lower() == 'y':
                            return area_number  # Return the extracted number
                        
                        else:
                            area_number = input('What is the correct area number? \t')
                            return area_number
            except Exception as e:
                print(f"Error processing message: {e}")
    print("No area information found.")
    area_number = input('What is the correct area number? \t')
    return area_number


def checkQuest(driver, keywords_good, keywords_bad, must_have_keyword="reward"):
    clear_screen()

    """
    Check the last 5 messages for keywords to determine if the quest is good or bad.

    Parameters:
        driver: WebDriver instance used to interact with the browser.
        keywords_good: List of keywords indicating a good quest.
        keywords_bad: List of keywords indicating a bad quest.
        must_have_keyword: A specific keyword (e.g., "reward") that must be present.

    Returns:
        questGood: True if any 'good' keyword is found and the must-have keyword is present,
                   False if any 'bad' keyword is found,
                   None if no relevant information is detected.
    """
    messages = driver.find_elements(by=By.CSS_SELECTOR, value="div[class^=message]")
    found_good = False
    found_bad = False
    found_must_have = False
    questContinue = True

    if len(messages) >= 5:
        lastMessages = messages[-5:]
        for msg in lastMessages:
            try:
                content = msg.find_element(by=By.CSS_SELECTOR, value="div[id^=message-content]")
                text = content.text.lower()  # Normalize text for case-insensitive matching

                # Check for the must-have keyword
                if must_have_keyword.lower() in text:
                    found_must_have = True

                # Check for other good keywords
                if any(keyword.lower() in text for keyword in keywords_good):
                    found_good = True

                # Check for bad keywords
                if any(keyword.lower() in text for keyword in keywords_bad):
                    found_bad = True  # Quest is bad; stop further checks

            except Exception as e:
                pass

    # Final evaluation based on findings
    if found_good and found_must_have:
        return True
        
    elif (found_good or found_bad) and not found_must_have:
        print("Quest incomplete")
        questContinue = input('cancel?\t')
        if questContinue == 'y':
            sendCommand(driver,"rpg quest quit")
        return None
    elif found_bad and found_must_have:
        return False
    else:
        return None


def heal(driver):
    sendCommand(driver, "rpg heal")

def sendCommand(driver, cmd):
    sendText(driver, cmd)
    time.sleep(2)
    if checkCaptcha(driver):
        for answer in captcha.solveCaptcha():
            sendText(driver, answer)

def menu():
    print('1 - hunt')
    print('2 - work command')
    print('3 - farm')
    print('4 - training')
    print('5 - adv')
    print('6 - quest')
    print('7 - daily etc')
    print('8 - misc')
    print('9 - tools')
    print('0 - settings')
    print('\n----------------------------------------------')
    choice = input('\n')
    return choice

def settingsMenu():
    clear_screen()
    print('1 - work cmd')
    print('2 - farming type')
    print(f'3 - toggle healing, {isHealing} ')
    print('\n----------------------------------------------')
    settingsChoice = input('\n')
    return settingsChoice

def miscMenu():
    clear_screen()
    print('more to come in the future')
    print('\n1 - lootbox')
    print('\n----------------------------------------------')
    miscChoice = input('\n')
    return miscChoice

def toolsMenu():
    clear_screen()
    print('more to come in the future')
    print('\n1 - trade tool')
    print('\n----------------------------------------------')
    toolsChoice = input('\n')
    return toolsChoice

def changeWorkCommand():
    clear_screen()
    while True:
        WORK_CMD = input('new work command:\t')
        print(f'new command is {WORK_CMD}')
        print('\n----------------------------------------------')

        confirm = input('\nconfirm?\t')
        if confirm.lower() == 'y':
            return WORK_CMD

def changeFarmCommand():
    clear_screen()
    while True:
        # FARM_CMD = input('new work command:\t')
        FARM_CMD += " " + input('which farm type')
        print(f'new command is {FARM_CMD}')
        print('\n----------------------------------------------')

        confirm = input('\nconfirm?\t')
        if confirm.lower() == 'y':
            return FARM_CMD

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')



###################################################
chromedriver_autoinstaller.install()

options = webdriver.ChromeOptions() 
options.add_argument(f"user-data-dir={DATA_DIR}")
options.add_argument(f'--profile-directory={PROFILE_DIR}')
driver = webdriver.Chrome(options=options)
driver.get(DISCORD_CHANNEL)
time.sleep(10)

lastRunWork = time.time()
inJail = False
isHealing = False


print('Welcome User')
print('\n----------------------------------------------')
print(f'\nHeal on hunt is {isHealing}')
print(f'Current hunt command is {HUNT_CMD}')
print(f'Current work command is {WORK_CMD}')
print(f'Current farm command is {FARM_CMD} \n')
print('\n----------------------------------------------')
ready = input('\nReady?')

if ready.lower() != 'ready':
    exit

while not killBot(driver):
    while not isInJail(driver) and not inJail:

        clear_screen()
        userChoice = menu()

        if userChoice == '0':
            settingsChose = settingsMenu()

            if settingsChose == '1':
                WORKCMD = changeWorkCommand()

            elif settingsChose == '2':
                FARM_CMD = changeFarmCommand()

            elif settingsChose == '3':
                
                if isHealing == True:
                    isHealing = False
                    print('Healing OFF')
                else: 
                    isHealing = True
                    print('Healing ON')

            else:
                print('wrong setings chose, looping back to start')
                time.sleep(1)
                print('In 3...')
                time.sleep(1)
                print('2...')
                time.sleep(1)
                print('1...')
                time.sleep(1)
                
        elif userChoice == '1':

            sendCommand(driver, HUNT_CMD)

            # isHealing = shouldBeHealing(driver)
            if isHealing:
                time.sleep(1 + random.uniform(0,2))
                heal(driver)

        elif userChoice == '2':
            sendCommand(driver, WORK_CMD)

        elif userChoice == '3':
            sendCommand(driver, FARM_CMD)

        elif userChoice == '4':
            sendCommand(driver, "rpg training")
            print('reply to the training')

            time.sleep(6)        
            # send pet command
            sendCommand(driver, "pat pat pat pat feed feed")

        elif userChoice == '5':
            sendCommand(driver, ADV_CMD)

        elif userChoice == '6':
            sendCommand(driver, "rpg quest")

            # Example keywords
            good_keywords = ["reward", "simple", "easy", "craft", "crafting", "join", "arena", "cook"]
            bad_keywords = ["summon", "miniboss", "guild", "raid", "kill", "gambling", "trade", "trading",]

            # Call the function with your driver
            questStatus = checkQuest(driver, good_keywords, bad_keywords)

            if questStatus is True:
               sendCommand(driver, "y")
            elif questStatus is False:
                sendCommand(driver, "n")

        elif userChoice == '7':
            daily_commands = ["daily", "weekly", "buy ed lb", "horse race", "big arena join"]

            for command in daily_commands:
                sendCommand(driver, f'rpg {command}')

        elif userChoice == '8':
            miscChose = miscMenu()
            
            if miscChose == '1':
                sendCommand(driver, "rpg buy ed lb")

            else:
                print('wrong setings chose, looping back to start')
                time.sleep(1)
                print('In 3...')
                time.sleep(1)
                print('2...')
                time.sleep(1)
                print('1...')
                time.sleep(1)

        elif userChoice == '9':   
            toolChose = toolsMenu()

            if toolChose == "1": 
                sendCommand(driver, "rpg p")
                currentArea = checkArea(driver)

                if currentArea == "1" or "2" or "3":
                    dismantle = []
                    trades = []

            else:
                print('wrong setings chose, looping back to start')
                time.sleep(1)
                print('In 3...')
                time.sleep(1)
                print('2...')
                time.sleep(1)
                print('1...')
                time.sleep(1)
                



    

    # sendCommand(driver, "Wake me up when the sentence ends")
    time.sleep(20)
    if backToWork(driver):
        inJail = False
        sendCommand(driver, "Messrs. Moony, Wormtail, Padfoot, and Prongs, Purveyors of Aids to Magical Mischief-Makers are proud to present Epic RPG Bot Bot.")
        
sendCommand(driver, "THE END")
driver.quit()

