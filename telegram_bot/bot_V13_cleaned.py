
import telebot
import config
import time
import schedule
import pyautogui
from datetime import timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

id_channel = "t.me/TimeSlotBooking_Bot"
bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=["start"])
def welcome(message):
    sti = open('/Users/vladimirlevchenko/DokumenterHD/programming/telegram_bot/static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    str = """Welcome, {0.first_name}!\n *BARK* \n <b>{1.first_name}</b> is here to book a time slot for you at Statens Vegvesen.\n
    Please type in one-by-one the following commands:
    🏁 <i>Refresh frequency</i>: how frequent to check the available time. Type in a number which corresponds to seconds. Default is 25 seconds.
    🕐 <i>Runtime</i>: How long do I have to check if the time slot is available. Specify number of hours (Default value is 2 hours).
    📚 <i>Book</i>: To book to the first available time slot.
    🚗 <i>Start searching</i>: Searching for an available time slot to book. Will send a message when I am done"""
    bot.send_message(message.chat.id, str.format(message.from_user, bot.get_me()),
    parse_mode="html")

@bot.message_handler(func=lambda m:True)
def echo_all(message):
    global running
    global notif
    global results
    if message.text == "Refresh frequency":
        bot.send_message(message.chat.id, "Type in the refresh frequency in seconds: ")
        bot.register_next_step_handler(message, func_refresh_frequency)
    if message.text == "Book":
        booking(results)
        bot.send_message(message.chat.id, "Booked. Good luck!")
    if message.text == "Runtime":
        bot.send_message(message.chat.id, "How long should I check (in hours)?")
        bot.register_next_step_handler(message, func_runtime)
    if message.text == "Start searching":
        sti_5 = open('/Users/vladimirlevchenko/DokumenterHD/programming/telegram_bot/static/searching.webp', 'rb')
        bot.send_sticker(message.chat.id, sti_5)
        bot.send_message(message.chat.id, "Let's do this! Performing search. *BARK*")

        # Start searching algorithm
        results = time_slot_check_Connection()
        # Run scheduled jobs
        schedule.every(refresh_seconds-2).seconds.until(timedelta(minutes=running_minutes)).do(search_check, message, results)
        schedule.every(refresh_seconds).seconds.until(timedelta(minutes=running_minutes)).do(refresh_function, message, results)
        notif = schedule.every(notification_time).seconds.until(timedelta(minutes=running_minutes)).do(notifications, message)

        # The while-loop is broken if False
        running = True
        while running:
            schedule.run_pending()
            if not schedule.jobs:
                break

        if running == True:
            sti_6 = open('/Users/vladimirlevchenko/DokumenterHD/programming/telegram_bot/static/notfound.webp', 'rb')
            bot.send_sticker(message.chat.id, sti_6)
            bot.send_message(message.chat.id, "Sorry, nothing found. *BARK*")

def time_slot_check_Connection():
    driver = webdriver.Chrome(
                executable_path = "/Users/vladimirlevchenko/DokumenterHD/programming/telegram_bot/chromedriver_2"
                )
    url = "https://www.vegvesen.no/dinside/?goto=https%3A%2F%2Fwww.vegvesen.no%2Fdinside%2Fdittforerkort%2Ftimebestilling%2F"

    response = driver.get(url)
    time.sleep(80) # waits till done logining

    # Reconnect to the opened web page
    new_html_source = driver.page_source
    return driver, new_html_source

def func_refresh_frequency(message):
    global refresh_seconds
    try:
        refresh_seconds = float(message.text)
        bot.send_message(message.chat.id, "Got it, *BARK*")
    except Exception:
        bot.send_message(message.chat.id, "It's not a number. Try again, *BARK*")

def func_runtime(message):
    global running_minutes
    try:
        running_hours = float(message.text)
        running_minutes = running_hours * 60
        bot.send_message(message.chat.id, "Got it, *BARK*")
    except Exception:
        bot.send_message(message.chat.id, "It's not a number. Try again, *BARK*")

def search_check(message, results):
    global running
    global refreshed_html
    global available_days
    global notif
    global soup

    count = 0
    # Reconnects to the open page in browser
    refreshed_html = results[0].page_source

    if "ingen ledige timer" in refreshed_html:
        count = count + 1
        print(count)
    if "Velg dato" in refreshed_html:
        sti_4 = open('/Users/vladimirlevchenko/DokumenterHD/programming/telegram_bot/static/found.webp', 'rb')
        bot.send_sticker(message.chat.id, sti_4)
        bot.send_message(message.chat.id, "FOUND! Go and book! *BARK* *BARK*")

        soup = BeautifulSoup(refreshed_html, 'html.parser')

        # This part returns the first available time slot to book
        rows = iter(soup.find_all("main", {"id": "hovedinnhold"}))
        for row in rows:
            a = row.find("div", class_="radiosjekk-kolonne")
            first_available_slot = a.find("div", class_="bottom-spacing-medium").text
            print(first_available_slot)

        bot.send_message(message.chat.id, first_available_slot)
        bot.send_message(message.chat.id, "Book? Type book.")

        # Turns of the jobs in the queue (stops the while loop)
        running = False

        # This part collects the available dates and saves them in a list
        available_days = []
        rows = soup.find_all("td", class_= "elm-kalender-dag elm-kalender-dag-velgbar")
        for row in rows:
            available_days.append(row.text)

        bot.send_message(message.chat.id, "Also the following dates are available:")
        scraped_days = scrape_all_dates()
        for y in scraped_days:
            bot.send_message(message.chat.id, f"Date: {y}{first_available_slot[-17:-9]}\nTime:{scraped_days[y]}")

def refresh_function(message, results):
    results[0].refresh()
    pyautogui.click(100, 100)
    print("Refreshed now")

def notifications(message):
    sti_7 = open('/Users/vladimirlevchenko/DokumenterHD/programming/telegram_bot/static/still_working.webp', 'rb')
    bot.send_sticker(message.chat.id, sti_7)
    bot.send_message(message.chat.id, "I am still searching. Stay stong! *BARK*")

def booking(results):
    results[0].execute_script("arguments[0].click();", WebDriverWait(results[0], 2).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='ledige-timer-0']"))))
    button = results[0].find_element_by_xpath('//button[@class="knapp knapp-neste knapp-handling"]')
    button.click()
    results[0].execute_script("arguments[0].click();", WebDriverWait(results[0], 2).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='bekreft']"))))
    button = results[0].find_element_by_xpath('//button[@class="knapp knapp-handling knapp-neste"]')
    button.click()

def scrape_all_dates():
    buttons = results[0].find_elements_by_css_selector("td")
    dict = {}

    for day in available_days:
        available_dates_list = []
        for button in buttons:
          if button.text.strip() == day:
            button.click()
            refreshed_html = results[0].page_source
            soup = BeautifulSoup(refreshed_html, 'html.parser')
            time.sleep(3)
            list_tags = iter(soup.find_all("label"))
            next(list_tags)
            for i in list_tags:
                available_dates_list.append(i.get_text())
                print(i.get_text())
            dict[day] = available_dates_list
    print(dict)
    return dict

if __name__ == "__main__":
    running_hours = 2 # default value
    running_minutes = running_hours * 60 # default value
    notification_time = round((running_minutes*60)//2) # default value
    refresh_seconds = 25 # Default value 25

    bot.polling(none_stop = True)
