# Exam-booking-BOT-for-Statens-Vegvesen-
A script that monitors the first available examination date with notifications in Telegram

## Background
Statens vegvesen is a norwegian institution that is responsible for roads, vehicle regulations and driver licencing. The latter will be the main focus of this project.
To obtain a driver licence, one must go thorough numerous mandatory driving hours, theory, and, of course, practical driving test. This final test (or exam if you wish) one must book via Statens Vegvesen's web page which unfortunately does not always offer that many spots available. In most of the times, there are no available dates to book and the only way to get an empty spot is to simply wait until someone else cancels his/her appointment so you can jump in.

The main advice from teachers in traffic schools is to refresh the Statens Vegvesen's examination page around 1000 time per day, and jump in to the time slot when available.  

🛠 **Problem**: lack of time to check when the available spot in the calender pops up;

💡 **Solution**: automate the checking routine and notify when the available spot appears!

## Code

Code's sections:
- connect to the webpage (autorization)
- web page scanning
- refresh and notification modules
- scrape the data when found
- book

Example code:
```Python
def refresh_function(message, results):
    results[0].refresh()
    pyautogui.click(100, 100)
    print("Refreshed now")
```
Challenges:
- authorization. Was overcame by setting a waiting time on ca 80 seconds - enough to login manually and choose the traffic school. When time is up, script recconects to the opened web page and continues to execute:

```Python
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
```
- wef
