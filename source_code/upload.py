# upload.py
from pathlib import Path
import subprocess, shutil, time

from appium import webdriver
from appium.options.android import UiAutomator2Options          # NEW import
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BST_SHARED = Path("/mnt/d/BlueStacks_nxt/Engine/UserData/SharedFolder")  # adjust to your path

_driver = None
def get_driver():
    global _driver
    if _driver:
        return _driver

    # 1️⃣  (re)connect to Bluestacks every time
    subprocess.run(["adb", "connect", "127.0.0.1:5555"], stdout=subprocess.DEVNULL)
    time.sleep(1)                           # tiny pause so adb lists it

    # 2️⃣  build modern options
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.device_name   = "Android"          # any non‑empty string
    opts.udid          = "127.0.0.1:5555"   # **key line**
    opts.app_package   = "com.zhiliaoapp.musically"
    opts.app_activity  = "com.ss.android.ugc.aweme.main.MainActivity"
    opts.no_reset      = True
    opts.new_command_timeout = 300

    _driver = webdriver.Remote(
        "http://127.0.0.1:4723/wd/hub",
        options=opts
    )
    _driver.implicitly_wait(10)
    return _driver


def upload_clip(mp4: Path, caption: str):
    drv = get_driver()

    shared_file = BST_SHARED / mp4.name
    shutil.copy(mp4, shared_file)

    drv.find_element(AppiumBy.ACCESSIBILITY_ID, "plus_button").click()
    drv.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Upload")'
    ).click()
    drv.find_element(AppiumBy.ID, "com.zhiliaoapp.musically:id/video_thumb").click()
    drv.find_element(AppiumBy.ID, "com.zhiliaoapp.musically:id/next").click()

    box = WebDriverWait(drv, 20).until(
        EC.presence_of_element_located(
            (AppiumBy.ID, "com.zhiliaoapp.musically:id/description_edit")
        )
    )
    box.send_keys(caption)
    drv.find_element(AppiumBy.ID, "com.zhiliaoapp.musically:id/post").click()
    time.sleep(5)
