from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
import os
import json
import sys
from os import walk
from sys import platform


with open('progress.json', 'w') as f:
    json.dump({"progress": "0"}, f)

OS_ENV = ("windows" if platform == "win32" else "linux")

ch = ""
if OS_ENV == "windows":
    ch = os.getcwd() + '/core/tools/chromedriver.exe'
else:
    ch = os.getcwd() + '/core/tools/chromedriver_linux'

try:
    os.mkdir(os.getcwd() + "\\core\\images\\" + sys.argv[1] + "-burned")
except:
    print("bad")
    exit()

options = Options()
options.add_argument("--headless")
options.add_argument("log-level=3")
options.add_argument("--incognito")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("prefs", {
  "download.default_directory": "akd",
  "download.prompt_for_download": False,
})

path = os.getcwd() + "\\core\\images\\" + sys.argv[1] + "-burned"


f = []
for (dirpath, dirnames, filenames) in walk(os.getcwd() + "/core/images/" + sys.argv[1]):
    f.extend(filenames)
    break

prevD = None

# sys.stdout.flush()

percent = 0
m = len(f)
each = 100 // m
part = each // 4
for filename in f:
    driver = webdriver.Chrome(options=options, executable_path=ch)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': path}}
    command_result = driver.execute("send_command", params)

    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(0.5)
    driver.get("https://burner.bonanza.com/home/login")
    driver.find_element_by_id("username").send_keys("sanzerinf@gmail.com")
    driver.find_element_by_id("user_password").send_keys("@nzCallahan1")
    driver.find_element_by_class_name("user_session_form_submit_button").click()
    i = driver.find_elements_by_css_selector("input[type='file']")[0]


    i.send_keys(os.getcwd() + "/core/images/" + sys.argv[1] + "/" + filename)

    while True:
        try:
            x = driver.find_elements_by_class_name("percent-complete")
            if len(x) != 0:
                upload = x[0]
                if "100" in upload.text:
                    percent += (part * 2)
                    with open('progress.json', 'w') as f:
                        json.dump({"progress": "{0}".format(percent)}, f)
                    break
        except:
            continue

    while True:
        try:
            x = driver.find_element_by_class_name("final_result_mask")
            break
        except:
            continue
    try:
        driver.find_element_by_class_name("download_button").click()
        percent += (part * 2)
        with open('progress.json', 'w') as f:
            json.dump({"progress": "{0}".format(percent)}, f)
    except:
        try:
            while True:
                try:
                    driver.find_element_by_class_name("touch_up_button").click()
                    break
                except:
                    continue
            while True:
                try:
                    save = driver.find_element_by_class_name("save")
                    percent += part
                    with open('progress.json', 'w') as f:
                        json.dump({"progress": "{0}".format(percent)}, f)
                    break
                except Exception:
                    print(Exception)
            time.sleep(10)
            driver.execute_script("document.getElementsByClassName('save')[0].click();")
            percent += part
            with open('progress.json', 'w') as f:
                json.dump({"progress": "{0}".format(percent)}, f)
            while True:
                try:
                    driver.find_element_by_class_name("download_button")
                    break
                except:
                    continue
            driver.find_element_by_class_name("download_button").click()
        except:
            print("bad")
            break
    if prevD == None:
        prevD = driver
    else:
        prevD.quit()
        prevD = driver
    
    
time.sleep(5)
prevD.quit()
with open('progress.json', 'w') as f:
    json.dump({"progress": "100"}, f)
print("done")

