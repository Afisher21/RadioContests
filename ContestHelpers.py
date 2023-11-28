from datetime import datetime
from selenium import webdriver

class ScheduledTime:
    """ Class to represent a scheduler.
        Notes:
            '*' : Represents 'all'. So could be every minute, every day, etc.
            '?' : Represents 'work time'. Monday-Friday, 9-5 depending on which field this is put into.
        Hours are in 24h format (14 == 2:00 pm)
        Minutes are standard 60 format
        Days are short-hand strings (Mon;Tues;Wed;Thur;Fri;Sat;Sun)
    """
    def __init__(self, day, hour, minute) -> None:
        self.day = day
        self.hour = hour
        self.minute = minute
        pass

    def ConvertToDateTime(self, now = datetime.now()):
        from datetime import timedelta

        target = now

        # Go ahead and set seconds to 0 since we don't support it anyways
        target = target.replace(second=0, microsecond=0)

        # Which minute is next valid?
        if self.minute == '*':
            # Target already contains now.
            pass
        else:
            if not isinstance(self.minute, int):
                raise Exception("Object is malformed! '" + self.minute + "' is not a valid number.")
            target = target.replace(minute=self.minute)

        # Which hour is next valid?
        if self.hour == '*':
            if target.minute < now.minute:
                # missed the one for this hour. Next valid is next hour
                target += timedelta(hours=1)
            else:
                target = target.replace(hour=now.hour)
        elif self.hour == '?':
            # 9 - 5
            if now.hour < 9:
                target = target.replace(hour=9)
            elif now.hour > 17:
                target = target.replace(hour=9)
                target = now + timedelta(days=1)
            else:
                if target.minute < now.minute:
                    if now.hour == 17:
                        # Have to go all the way to tomorrow for the next valid time
                        target = target.replace(hour=9)
                        target = now + timedelta(days=1)
                    else:
                        # Missed the one for this hour. Next valid is next hour
                        target += timedelta(hours=1)
                else:
                    target = target.replace(hour=now.hour)
        else:
            target = target.replace(hour=self.hour)
        
        # Which day is next valid?
        if self.day == '*':
            # If the hour already passed for today, lets point at tomorrow
            if target.hour < now.hour:
                target += timedelta(days=1)
            pass
        elif self.day == '?':
            curr_weekday = now.weekday()
            if curr_weekday < 5:
                target = target.replace(day=now.day)
            elif curr_weekday == 5:
                target = target.replace(day= now +  timedelta(days=2))
            elif curr_weekday == 6:
                target = target.replace(day= now +  timedelta(days=1))
        else:
            # Have to parse the string for which days are supported
            raise Exception("Not supported yet")
        
        return target            

class Competition:
    """
        Defines a radio competition.
        Times is a list of times the competition is held
        fnc is a function to call when the timer is active
    """
    def __init__(self, title: str, times: list, fnc) -> None:
        self.Title = title
        self.Times = times
        self.Action = fnc

    def AddExpiry(self, datetime):
        self.Expiration = datetime

from collections.abc import Sequence

def RemoveExpiredCompetitions(competitions: Sequence[Competition]):
    now = datetime.now()
    # For each competition, we should see if it has expired
    for contest in competitions:
        if hasattr(contest, 'Expiration'):
            if now > contest.Expiration:
                # Must remove this contest from the competitions list
                print("Found an expired contest :(. Please remove '" + contest.Title + "' from the array.")
                competitions.remove(contest)
    
    return competitions

def HandleCompetitionLoop(competitions: Sequence[Competition]) -> None:
    from datetime import timedelta
    import time
    import pyautogui

    while True:
        # Validate that the contests are still running
        valid_competitions = RemoveExpiredCompetitions(competitions)

        # Convert to today's time stamps. Prevents us having to recalculate every loop
        # Remove any time that has already expired
        now = datetime.now()
        for contest in valid_competitions:
            times = []
            for attempt in contest.Times:
                tm = attempt.ConvertToDateTime()
                if now < tm:
                    times.append(tm)
            contest.Times = times
        
        while len(valid_competitions) > 0:
            now = datetime.now()
            next_contest_time = now + timedelta(days=7)
            next_contest = Competition('N/A',[],'')            

            valid_competitions = [comp for comp in valid_competitions if len(comp.Times) > 0]

            # Find the closest competition time (iterate through all in case the times aren't sorted)
            for contest in valid_competitions:
                for instance in contest.Times:
                
                    # This is an upcoming contest. But is it the soonest upcoming one?
                    if instance < next_contest_time:
                                next_contest_time = instance
                                next_contest = contest
            
            # Now that we know which will happen next, let's sleep until that time
            print('Next event: "' + next_contest.Title + '", at ' + str(next_contest_time))
            sleep_seconds = next_contest_time - datetime.now()
            time.sleep(sleep_seconds.total_seconds())

            # Convenience wrapper - sends keyboard 'stop' which should work on any desktop apps
            pyautogui.press('stop')
            # Invoke the registered action for this contest
            next_contest.Action()
            next_contest.Times.remove(next_contest_time)
            # Send keyboard 'play' which should resume ... probably.
            pyautogui.press('playpause')
        
        # That's all for today folks
        print("No more radio contests today. Sleeping until tomorrow")
        tomorrow = now + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=1, minute=0, second=0,microsecond=0)
        sleep_seconds = tomorrow - datetime.now()
        time.sleep(sleep_seconds.total_seconds())

def WaitForKeyword(driver: webdriver) -> None:
    import time
    # Give the user some time to listen for the keyword (5 * 100 = 500s = ~8 minutes)
    # if they get bored and exit early, that's also fine
    for i in range(100):
        # Sleep 5 seconds, then check if driver is still open.
        time.sleep(5)
        # literally anything that exercises the driver is fine here. If the driver is closed, an exception is detected and handled
        try:
            current_url = driver.current_url
        except:
            print('User closed driver.')
            break

def RecordAudio(outFile: str, seconds: int) -> None:
    import wave
    import sys
    import pyaudio

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 #if sys.platform == 'darwin' else 2
    RATE = 44100
    RECORD_SECONDS = seconds

    with wave.open(outFile, 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print('Recording...')
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
        print('Done')

        stream.close()
        p.terminate()

def LaunchGenericListenNow(url:str, listen_xpath:str) -> webdriver:
    """Wrapper to automatically launch a URL and click it's "listen now" button

    Args:
        url (string): URL for the website
        listen_xpath (XPATH string): XPATH to use to look for the "listen now" button

    Returns:
        selenium.webdriver: Handle for the driver. Caller must close
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        # Launch Driver
        driver = webdriver.Firefox()
        driver.get(url)

        # Look for 'listen now' button
        listen_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, listen_xpath))
        )
        
        # Click the provided button
        listen_btn.click()
    except:
        driver.quit()
        raise
    
    # Return the driver to caller. 
    return driver


########################################
#
# Unit testing
#
#######################################

import unittest

class _TestScheduledTime(unittest.TestCase):
    from datetime import datetime
    
    def test_schedulerMinuteRoll(self):
        sample_workday = datetime(year=2023, month=10, day=23, hour=10, minute=9)
        roll_hour = ScheduledTime("*", "*", sample_workday.minute - 1)
        next = roll_hour.ConvertToDateTime(sample_workday)

        # Scheduled for right time after hour
        print("Next time: (" + str(next.day), str(next.hour), str(next.minute) + ")")
        self.assertEqual(sample_workday.minute - 1, next.minute, "Time should be at the 10 after")
        self.assertEqual(sample_workday.hour + 1, next.hour, "If curr time is after the window, next hit is next hour")
        self.assertEqual(sample_workday.day, next.day)
    
    def test_schedulerHourRoll(self):
        sample_workday = datetime(year=2023, month=10, day=23, hour=10, minute=9)
        roll_day = ScheduledTime("*", 9, sample_workday.minute)
        next = roll_day.ConvertToDateTime(sample_workday)

        print("Next time: (" + str(next.day), str(next.hour), str(next.minute) + ")")
        self.assertEqual(sample_workday.minute, next.minute, "Minute shouldn't be changed")
        self.assertEqual(roll_day.hour, next.hour, "hour shouldn't be changed")
        self.assertEqual(sample_workday.day + 1, next.day, "If that hour was missed, the next available is tomorrow")



        

if __name__ == '__main__':
    unittest.main()