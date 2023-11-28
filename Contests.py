##################################################################################################################
#
#                                Current competitions
#
##################################################################################################################
from ContestHelpers import *

def LaunchBj1000():
    # Launch the url and click the 'listen now' button
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    url = "https://live.movin925.com/listen/"

    try:
        driver = webdriver.Firefox()
        driver.get(url)

        # The play button is a bit funky, so either we find the <slightly less fragile> wrapper and drill down or find the random ember-action directly
        #play_btn = driver.find_element(By.XPATH, "//a[@data-ember-action='672']")
        wrapper = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'hll-actions-listen')]"))
        )
        play_btn = wrapper.find_element(By.XPATH, "a")
        play_btn.click() 
        
        WaitForKeyword(driver)

    finally:
        # Always close the driver afterwards
        driver.quit()

def Bj1000NameGame():
    # Names are always read 10 after, so set for 8 minutes to account for songs
    times = []

    for i in [7,8,12,14,17]:
        times.append(ScheduledTime('?', i, 8))

    return Competition("Brooke and Jeffrey's $1000 name game", times, LaunchBj1000)

def LaunchTheSound():
    # Launch the url and click the 'listen now' button
    from selenium import webdriver

    url = "https://www.audacy.com/stations/941thesoundseattle"
    contest_page = "https://www.audacy.com/941thesoundseattle/contests/your-chance-to-win-jonas-brothers-tickets-on-94-1-the-sound"

    driver = LaunchGenericListenNow(url, "//button[@aria-label='Listen to Live']")

    try:
        # Open contest page
        driver.switch_to.new_window('tab')
        driver.get(contest_page)

        emails = ['crazyfisher21@gmail.com', 'isabellaspaletta@yahoo.com']
        # these guys are CRAZY good about making this a huge pita to parse with the driver.
        WaitForKeyword(driver)

    finally:
        # make sure we always gracefully close the driver
        driver.quit()


def TheSoundJoBros():
    from datetime import datetime
    times = []
    # 7 am to 8 pm
    for i in range(7,20):
        # codes read at 25 after
        times.append(ScheduledTime('?', i, 23))
    
    comp = Competition("The sound Jonas brothers tickets", times, LaunchTheSound)
    comp.AddExpiry(datetime(year=2023, month=11, day=3, hour=21))

    return comp

def LaunchStar1015():
    """Launcher for "Star 101.5 Seattle"
    """

    driver = LaunchGenericListenNow("https://www.star1015.com/", "//*[name()='svg' and contains(@class,'audio-player-open-flyout')]")

    try:
        # This is a 'text to enter' so no contest page
        WaitForKeyword(driver)

    finally:
        # make sure we always gracefully close the driver
        driver.quit()

def StarDisneyland():
    """Contest handler for the "Disneyland trip" on Star 101.5

    Returns:
        Competition: Competition info including the listen now launcher & times that keywords are read
    """
    from datetime import datetime
    times = []
    
    # Notes read on the hour at 8,11,13,15
    for t in iter([8,11,13,15]):
        times.append(ScheduledTime('?', t - 1, 58))

    comp = Competition("Star 101.5 Trip to disneyland", times, LaunchStar1015)
    comp.AddExpiry(datetime(year=2023, month=12, day=12))
    
    return comp

########################################
#
# Unit testing
#
#######################################

import unittest, unittest.mock

class ContestValidation(unittest.TestCase):
    """Unit tests to validate that launching "Listen now" buttons works properly

    Notes:
        WaitForKeyword is mocked so that if the listen button works, the driver doesn't wait for 5 minutes
    Args:
        unittest (_type_): _description_
    """
    #@unittest.mock.patch('helpers.WaitForKeyword')
    def test_Star1015Listen(self):
        #mocked.return_value = None
        LaunchStar1015()
    def test_Movin925Listen(self):
        #mocked.return_value = None
        LaunchBj1000()
    def test_TheSoundListen(self):
        LaunchTheSound()

        

if __name__ == '__main__':
    unittest.main()
