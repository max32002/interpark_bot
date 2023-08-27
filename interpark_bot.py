#!/usr/bin/env python3
#encoding=utf-8
# seleniumwire not support python 2.x.
# if you want running under python 2.x, you need to assign driver_type = 'stealth'
import os
import pathlib
import sys
import platform
import json
import random

from selenium import webdriver
# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# for selenium 4
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
# for wait #1
import time
# for error output
import logging
logging.basicConfig()
logger = logging.getLogger('logger')
# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ocr
import base64
try:
    import ddddocr
    #PS: python 3.11.1 raise PIL conflict.
    from NonBrowser import NonBrowser
except Exception as exc:
    pass

import argparse
import chromedriver_autoinstaller

CONST_APP_VERSION = "Max Interpark Bot (2023.08.11)"

CONST_MAXBOT_CONFIG_FILE = 'settings.json'
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"

CONST_HOMEPAGE_DEFAULT = "https://www.globalinterpark.com/"
CONST_INTERPARK_SIGN_IN_URL = "https://www.globalinterpark.com/user/signin"

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"

def t_or_f(arg):
    ret = False
    ua = str(arg).upper()
    if 'TRUE'.startswith(ua):
        ret = True
    elif 'YES'.startswith(ua):
        ret = True
    return ret

def sx(s1):
    key=18
    return ''.join(chr(ord(a) ^ key) for a in s1)

def decryptMe(b):
    s=""
    if(len(b)>0):
        s=sx(base64.b64decode(b).decode("UTF-8"))
    return s

def encryptMe(s):
    data=""
    if(len(s)>0):
        data=base64.b64encode(sx(s).encode('UTF-8')).decode("UTF-8")
    return data

def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_config_dict(args):
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    # allow assign config by command line.
    if not args.input is None:
        if len(args.input) > 0:
            config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    return config_dict

def write_last_url_to_file(url):
    outfile = None
    if platform.system() == 'Windows':
        outfile = open(CONST_MAXBOT_LAST_URL_FILE, 'w', encoding='UTF-8')
    else:
        outfile = open(CONST_MAXBOT_LAST_URL_FILE, 'w')

    if not outfile is None:
        outfile.write("%s" % url)

def read_last_url_from_file():
    ret = ""
    with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
        ret = text_file.readline()
    return ret

def get_favoriate_extension_path(webdriver_path):
    print("webdriver_path:", webdriver_path)
    extension_list = []
    extension_list.append(os.path.join(webdriver_path,"Adblock_3.18.1.0.crx"))
    extension_list.append(os.path.join(webdriver_path,"Buster_2.0.1.0.crx"))
    extension_list.append(os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx"))
    extension_list.append(os.path.join(webdriver_path,"proxy-switchyomega_2.5.21.0.crx"))
    return extension_list

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_brave_bin_path():
    brave_path = ""
    if platform.system() == 'Windows':
        brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if not os.path.exists(brave_path):
            brave_path = os.path.expanduser('~') + "\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if not os.path.exists(brave_path):
            brave_path = "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if not os.path.exists(brave_path):
            brave_path = "D:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"

    if platform.system() == 'Linux':
        brave_path = "/usr/bin/brave-browser"

    if platform.system() == 'Darwin':
        brave_path = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'

    return brave_path

def get_chrome_options(webdriver_path, adblock_plus_enable, browser="chrome", headless = False):
    chrome_options = webdriver.ChromeOptions()
    if browser=="edge":
        chrome_options = webdriver.EdgeOptions()
    if browser=="safari":
        chrome_options = webdriver.SafariOptions()

    # some windows cause: timed out receiving message from renderer
    if adblock_plus_enable:
        # PS: this is ocx version.
        extension_list = get_favoriate_extension_path(webdriver_path)
        for ext in extension_list:
            if os.path.exists(ext):
                chrome_options.add_extension(ext)
    if headless:
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument("--no-sandbox");

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    if browser=="brave":
        brave_path = get_brave_bin_path()
        if os.path.exists(brave_path):
            chrome_options.binary_location = brave_path

    chrome_options.page_load_strategy = 'eager'
    #chrome_options.page_load_strategy = 'none'
    chrome_options.unhandled_prompt_behavior = "accept"

    return chrome_options

def load_chromdriver_normal(config_dict, driver_type):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    driver = None

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("WebDriver not exist, try to download to:", webdriver_path)
        chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
    else:
        print("ChromeDriver exist:", chromedriver_path)

    if not os.path.exists(chromedriver_path):
        print("Please download chromedriver and extract zip to webdriver folder from this url:")
        print("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        print(URL_CHROME_DRIVER)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict["advanced"]["adblock_plus_enable"], browser=config_dict["browser"], headless=config_dict["advanced"]["headless"])
        try:
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            if show_debug_message:
                print(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

                # remove exist chromedriver, download again.
                try:
                    print("Deleting exist and download ChromeDriver again.")
                    os.unlink(chromedriver_path)
                except Exception as exc2:
                    print(exc2)
                    pass

                chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
                chrome_service = Service(chromedriver_path)
                try:
                    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
                except Exception as exc2:
                    print("Selenium 4.11.0 Release with Chrome For Testing Browser.")
                    try:
                        driver = webdriver.Chrome(service=Service(), options=chrome_options)
                    except Exception as exc3:
                        print(exc3)
                        pass

    if driver_type=="stealth":
        from selenium_stealth import stealth
        # Selenium Stealth settings
        stealth(driver,
              languages=["zh-TW", "zh"],
              vendor="Google Inc.",
              platform="Win32",
              webgl_vendor="Intel Inc.",
              renderer="Intel Iris OpenGL Engine",
              fix_hairline=True,
          )
    #print("driver capabilities", driver.capabilities)

    return driver

def clean_uc_exe_cache():
    exe_name = "chromedriver%s"

    platform = sys.platform
    if platform.endswith("win32"):
        exe_name %= ".exe"
    if platform.endswith(("linux", "linux2")):
        exe_name %= ""
    if platform.endswith("darwin"):
        exe_name %= ""

    d = ""
    if platform.endswith("win32"):
        d = "~/appdata/roaming/undetected_chromedriver"
    elif "LAMBDA_TASK_ROOT" in os.environ:
        d = "/tmp/undetected_chromedriver"
    elif platform.startswith(("linux", "linux2")):
        d = "~/.local/share/undetected_chromedriver"
    elif platform.endswith("darwin"):
        d = "~/Library/Application Support/undetected_chromedriver"
    else:
        d = "~/.undetected_chromedriver"
    data_path = os.path.abspath(os.path.expanduser(d))

    is_cache_exist = False
    p = pathlib.Path(data_path)
    files = list(p.rglob("*chromedriver*?"))
    for file in files:
        if os.path.exists(str(file)):
            is_cache_exist = True
            try:
                os.unlink(str(file))
            except Exception as exc2:
                print(exc2)
                pass

    return is_cache_exist

def load_chromdriver_uc(config_dict):
    import undetected_chromedriver as uc

    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("ChromeDriver not exist, try to download to:", webdriver_path)
        chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
    else:
        print("ChromeDriver exist:", chromedriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    #options.page_load_strategy = 'none'
    options.unhandled_prompt_behavior = "accept"

    #print("strategy", options.page_load_strategy)

    if config_dict["advanced"]["adblock_plus_enable"]:
        load_extension_path = ""
        extension_list = get_favoriate_extension_path(webdriver_path)
        for ext in extension_list:
            ext = ext.replace('.crx','')
            if os.path.exists(ext):
                load_extension_path += ("," + os.path.abspath(ext))
        if len(load_extension_path) > 0:
            print('load-extension:', load_extension_path[1:])
            options.add_argument('--load-extension=' + load_extension_path[1:])

    if config_dict["advanced"]["headless"]:
        #options.add_argument('--headless')
        options.add_argument('--headless=new')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')
    options.add_argument('--disable-web-security')
    options.add_argument("--no-sandbox");

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    if config_dict["browser"]=="brave":
        brave_path = get_brave_bin_path()
        if os.path.exists(brave_path):
            options.binary_location = brave_path

    driver = None
    if os.path.exists(chromedriver_path):
        # use chromedriver_autodownload instead of uc auto download.
        is_cache_exist = clean_uc_exe_cache()

        try:
            driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options, headless=config_dict["advanced"]["headless"])
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

            # remove exist chromedriver, download again.
            try:
                print("Deleting exist and download ChromeDriver again.")
                os.unlink(chromedriver_path)
            except Exception as exc2:
                print(exc2)
                pass

            chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
            try:
                driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options, headless=config_dict["advanced"]["headless"])
            except Exception as exc2:
                pass
    else:
        print("WebDriver not found at path:", chromedriver_path)

    if driver is None:
        print('WebDriver object is None..., try again..')
        try:
            driver = uc.Chrome(options=options, headless=config_dict["advanced"]["headless"])
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
            pass

    if driver is None:
        print("create web drive object by undetected_chromedriver fail!")

        if os.path.exists(chromedriver_path):
            print("Unable to use undetected_chromedriver, ")
            print("try to use local chromedriver to launch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(config_dict, driver_type)
        else:
            print("建議您自行下載 ChromeDriver 到 webdriver 的資料夾下")
            print("you need manually download ChromeDriver to webdriver folder.")

    return driver

def close_browser_tabs(driver):
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def get_driver_by_config(config_dict):
    global driver

    # read config.
    homepage = config_dict["homepage"]

    if not config_dict is None:
        # output config:
        print("maxbot app version", CONST_APP_VERSION)
        print("python version", platform.python_version())
        print("homepage", config_dict["homepage"])
        
        homepage = config_dict["homepage"]

    # entry point
    if homepage is None:
        homepage = ""
    if len(homepage) == 0:
        homepage = CONST_HOMEPAGE_DEFAULT

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())

    if config_dict["browser"] in ["chrome","brave"]:
        # method 6: Selenium Stealth
        if config_dict["webdriver_type"] != CONST_WEBDRIVER_TYPE_UC:
            driver = load_chromdriver_normal(config_dict, config_dict["webdriver_type"])
        else:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(config_dict)

    if config_dict["browser"] == "firefox":
        # default os is linux/mac
        # download url: https://github.com/mozilla/geckodriver/releases
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

        if "macos" in platform.platform().lower():
            if "arm64" in platform.platform().lower():
                chromedriver_path = os.path.join(webdriver_path,"geckodriver_arm")

        webdriver_service = Service(chromedriver_path)
        driver = None
        try:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if config_dict["advanced"]["headless"]:
                options.add_argument('--headless')
                #options.add_argument('--headless=new')
            if platform.system().lower()=="windows":
                binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = os.path.expanduser('~') + "\\AppData\\Local\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "D:\\Program Files\\Mozilla Firefox\\firefox.exe"
                options.binary_location = binary_path

            driver = webdriver.Firefox(service=webdriver_service, options=options)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)
            else:
                print(exc)

    if config_dict["browser"] == "edge":
        # default os is linux/mac
        # download url: https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")

        webdriver_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict["advanced"]["adblock_plus_enable"], browser="edge", headless=config_dict["advanced"]["headless"])

        driver = None
        try:
            driver = webdriver.Edge(service=webdriver_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if config_dict["browser"] == "safari":
        driver = None
        try:
            driver = webdriver.Safari()
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            print("goto url:", homepage)

            if 'globalinterpark.com' in homepage:
                if len(config_dict["advanced"]["interpark_account"])>0:
                    homepage = CONST_INTERPARK_SIGN_IN_URL

            driver.get(homepage)
            time.sleep(3.0)
        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
        except Exception as exce1:
            print('get URL Exception:', exce1)
            pass

    return driver

def get_current_url(driver):
    DISCONNECTED_MSG = ': target window already closed'

    url = ""
    is_quit_bot = False

    try:
        url = driver.current_url
    except NoSuchWindowException:
        print('NoSuchWindowException at this url:', url )
        #print("last_url:", last_url)
        #print("get_log:", driver.get_log('driver'))
        window_handles_count = 0
        try:
            window_handles_count = len(driver.window_handles)
            #print("window_handles_count:", window_handles_count)
            if window_handles_count >= 1:
                driver.switch_to.window(driver.window_handles[0])
                driver.switch_to.default_content()
                time.sleep(0.2)
        except Exception as excSwithFail:
            #print("excSwithFail:", excSwithFail)
            pass
        if window_handles_count==0:
            try:
                driver_log = driver.get_log('driver')[-1]['message']
                print("get_log:", driver_log)
                if DISCONNECTED_MSG in driver_log:
                    print('quit bot by NoSuchWindowException')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()
            except Exception as excGetDriverMessageFail:
                #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                except_string = str(excGetDriverMessageFail)
                if 'HTTP method not allowed' in except_string:
                    print('quit bot by close browser')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

    except UnexpectedAlertPresentException as exc1:
        print('UnexpectedAlertPresentException at this url:', url )
        # PS: do nothing...
        # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
        # raise exception at selenium/webdriver/remote/errorhandler.py
        # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
        is_pass_alert = False
        is_pass_alert = True
        if is_pass_alert:
            try:
                driver.switch_to.alert.accept()
            except Exception as exc:
                pass

    except Exception as exc:
        logger.error('Maxbot URL Exception')
        logger.error(exc, exc_info=True)

        #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
        str_exc = ""
        try:
            str_exc = str(exc)
        except Exception as exc2:
            pass

        if len(str_exc)==0:
            str_exc = repr(exc)

        exit_bot_error_strings = ['Max retries exceeded'
        , 'chrome not reachable'
        , 'unable to connect to renderer'
        , 'failed to check if window was closed'
        , 'Failed to establish a new connection'
        , 'Connection refused'
        , 'disconnected'
        , 'without establishing a connection'
        , 'web view not found'
        , 'invalid session id'
        ]
        for each_error_string in exit_bot_error_strings:
            if isinstance(str_exc, str):
                if each_error_string in str_exc:
                    print('quit bot by error:', each_error_string)
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

        # not is above case, print exception.
        print("Exception:", str_exc)
        pass

    return url, is_quit_bot

def format_keyword_string(keyword):
    if not keyword is None:
        if len(keyword) > 0:
            keyword = keyword.replace('／','/')
            keyword = keyword.replace('　','')
            keyword = keyword.replace(',','')
            keyword = keyword.replace('，','')
            keyword = keyword.replace('$','')
            keyword = keyword.replace(' ','').lower()
    return keyword

def force_press_button_iframe(driver, f, select_by, select_query, force_submit=True):
    if not f:
        # ensure we are on main content frame
        try:
            driver.switch_to.default_content()
        except Exception as exc:
            pass
    else:
        try:
            driver.switch_to.frame(f)
        except Exception as exc:
            pass

    is_clicked = force_press_button(driver, select_by, select_query, force_submit)

    if f:
        # switch back to main content, otherwise we will get StaleElementReferenceException
        try:
            driver.switch_to.default_content()
        except Exception as exc:
            pass

    return is_clicked

def check_checkbox(driver, by, query):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    agree_checkbox = None
    try:
        agree_checkbox = driver.find_element(by, query)
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass
    is_checkbox_checked = False
    if agree_checkbox is not None:
        is_checkbox_checked = force_check_checkbox(driver, agree_checkbox)
    return is_checkbox_checked

def force_check_checkbox(driver, agree_checkbox):
    is_finish_checkbox_click = False
    if agree_checkbox is not None:
        is_visible = False
        try:
            if agree_checkbox.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            is_checkbox_checked = False
            try:
                if agree_checkbox.is_selected():
                    is_checkbox_checked = True
            except Exception as exc:
                pass

            if not is_checkbox_checked:
                #print('send check to checkbox')
                try:
                    agree_checkbox.click()
                    is_finish_checkbox_click = True
                except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", agree_checkbox)
                        is_finish_checkbox_click = True
                    except Exception as exc:
                        pass
            else:
                is_finish_checkbox_click = True
    return is_finish_checkbox_click

def force_press_button(driver, select_by, select_query, force_submit=True):
    is_clicked = False
    next_step_button = None
    try:
        next_step_button = driver.find_element(select_by ,select_query)
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                is_clicked = True
    except Exception as exc:
        #print("find %s clickable Exception:" % (select_query))
        #print(exc)
        pass

        if force_submit:
            if not next_step_button is None:
                is_visible = False
                try:
                    if next_step_button.is_enabled():
                        is_visible = True
                except Exception as exc:
                    pass

                if is_visible:
                    try:
                        driver.set_script_timeout(1)
                        driver.execute_script("arguments[0].click();", next_step_button)
                        is_clicked = True
                    except Exception as exc:
                        pass
    return is_clicked

def assign_select_by_text(driver, by, query, val):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if val is None:
        val = ""

    is_text_sent = False
    if len(val) > 0:
        el_text = None
        try:
            el_text = driver.find_element(by, query)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        select_obj = None
        if el_text is not None:
            try:
                if el_text.is_enabled() and el_text.is_displayed():
                    select_obj = Select(el_text)
                    if not select_obj is None:
                        select_obj.select_by_visible_text(val)
                        is_text_sent = True
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass
            
    return is_text_sent

def assign_text(driver, by, query, val, overwrite = False, submit=False):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if val is None:
        val = ""

    is_visible = False

    if len(val) > 0:
        el_text = None
        try:
            el_text = driver.find_element(by, query)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if el_text is not None:
            try:
                if el_text.is_enabled() and el_text.is_displayed():
                    is_visible = True
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass

    is_text_sent = False
    if is_visible:
        try:
            inputed_text = el_text.get_attribute('value')
            if inputed_text is not None:
                is_do_keyin = False
                if len(inputed_text) == 0:
                    is_do_keyin = True
                else:
                    if inputed_text == val:
                        is_text_sent = True
                    else:
                        if overwrite:
                            el_text.clear()
                            is_do_keyin = True

                if is_do_keyin:
                    el_text.click()
                    el_text.send_keys(val)
                    if submit:
                        el_text.send_keys(Keys.ENTER)
                    is_text_sent = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass
            
    return is_text_sent


def facebook_login(driver, account, password):
    is_email_sent = assign_text(driver, By.CSS_SELECTOR, '#email', account)
    is_password_sent = False
    if is_email_sent:
        is_password_sent = assign_text(driver, By.CSS_SELECTOR, '#pass', password, submit=True)
    return is_password_sent

def interpark_get_local_code(locale_title):
    code = "en"
    if locale_title == "locale":
        code = "ko"
    if locale_title == "中文":
        code = "zh-cn"
    if locale_title == "日本語":
        code = "ja"
    return code

def interpark_change_locale(driver, config_dict):
    el_locale = None
    try:
        el_locale = driver.find_element(By.CSS_SELECTOR, '#lang_title')
        current_locale = el_locale.text
        if len(current_locale) > 0:
            if config_dict["locale"] != current_locale:
                local_code = interpark_get_local_code(config_dict["locale"])
                js = "fnc_changeLocale('%s');" % (local_code)
                driver.set_script_timeout(1)
                driver.execute_script(js)
                time.sleep(0.2)
    except Exception as exc:
        print(exc)
        pass

def search_iframe(driver, f, by, value):
    elem = None
    if not f:
        # ensure we are on main content frame
        try:
            driver.switch_to.default_content()
            elem = driver.find_elements(by, value)
        except Exception as exc:
            pass
    else:
        try:
            driver.switch_to.frame(f)
            elem = driver.find_elements(by, value)
        except Exception as exc:
            print(exc)
            pass
        # switch back to main content, otherwise we will get StaleElementReferenceException
        try:
            driver.switch_to.default_content()
        except Exception as exc:
            pass
    return elem

def get_matched_blocks_by_keyword_item_set(config_dict, auto_select_mode, keyword_item_set, formated_area_list):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    matched_blocks = []
    for row in formated_area_list:
        row_text = ""
        try:
            row_text = row.text
        except Exception as exc:
            pass
        if row_text is None:
            row_text = ""
        if len(row_text) > 0:
            if reset_row_text_if_match_keyword_exclude(config_dict, row_text):
                row_text = ""
        if len(row_text) > 0:
            if show_debug_message:
                print("row_text:", row_text)

            is_match_all = False
            if ' ' in keyword_item_set:
                keyword_item_array = keyword_item_set.split(' ')
                is_match_all = True
                for keyword_item in keyword_item_array:
                    keyword_item = format_keyword_string(keyword_item)
                    if not keyword_item in row_text:
                        is_match_all = False
            else:
                exclude_item = format_keyword_string(keyword_item_set)
                if exclude_item in row_text:
                    is_match_all = True

            if is_match_all:
                matched_blocks.append(row)

                # only need first row.
                if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    break
    return matched_blocks

def get_matched_blocks_by_keyword(config_dict, auto_select_mode, keyword_string, formated_area_list):
    keyword_array = []
    try:
        keyword_array = json.loads("["+ keyword_string +"]")
    except Exception as exc:
        keyword_array = []

    matched_blocks = []
    for keyword_item_set in keyword_array:
        matched_blocks = get_matched_blocks_by_keyword_item_set(config_dict, auto_select_mode, keyword_item_set, formated_area_list)
        if len(matched_blocks) > 0:
            break
    return matched_blocks

def is_row_match_keyword(keyword_string, row_text):
    # clean stop word.
    row_text = format_keyword_string(row_text)

    is_match_keyword = False
    if len(keyword_string) > 0:
        area_keyword_exclude_array = []
        try:
            area_keyword_exclude_array = json.loads("["+ keyword_string +"]")
        except Exception as exc:
            area_keyword_exclude_array = []
        for exclude_item_list in area_keyword_exclude_array:
            if len(row_text) > 0:
                if ' ' in exclude_item_list:
                    area_keyword_array = exclude_item_list.split(' ')
                    is_match_all_exclude = True
                    for exclude_item in area_keyword_array:
                        exclude_item = format_keyword_string(exclude_item)
                        if not exclude_item in row_text:
                            is_match_all_exclude = False
                    if is_match_all_exclude:
                        row_text = ""
                        is_match_keyword = True
                        break
                else:
                    exclude_item = format_keyword_string(exclude_item_list)
                    if exclude_item in row_text:
                        row_text = ""
                        is_match_keyword = True
                        break
    return is_match_keyword

def reset_row_text_if_match_keyword_exclude(config_dict, row_text):
    area_keyword_exclude = config_dict["keyword_exclude"]
    return is_row_match_keyword(area_keyword_exclude, row_text)

def interpart_date_auto_select(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    if show_debug_message:
        print("date_keyword:", config_dict["date_auto_select"]["date_keyword"])

    is_select_exist = False

    my_css_selector = '#play_date'
    form_select = None
    select_obj = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if form_select is not None:
            select_obj = Select(form_select)
            if not select_obj is None:
                is_select_exist = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    area_list = None
    if is_select_exist:
        try:
            area_list = select_obj.options
        except Exception as exc:
            pass

    is_date_assign_by_bot = False
    if not area_list is None:
        if show_debug_message:
            print("len(area_list):", len(area_list))
        if len(area_list) > 0:
            is_select_exist = True

            if len(area_list) == 1:
                # first time.
                if show_debug_message:
                    print('click on date select box, to get date list')
                
                # skip this round wait ajax return.
                area_list = None
                try:
                    act = ActionChains(driver)
                    act.move_to_element(form_select).perform()

                    form_select.click()
                    time.sleep(0.1)
                    form_select.click()
                except Exception as exc:
                    pass
            else:
                # normal case.
                option_value = ""
                try:
                    selected_option = select_obj.first_selected_option
                    option_value = selected_option.get_attribute('value')
                except Exception as exc:
                    pass
                if option_value is None:
                    option_value = ""
                if len(option_value) > 0:
                    print("date is selected.")
                    area_list = None
                    is_date_assign_by_bot = True

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                # default is enabled.
                row_is_enabled=True

                if row_is_enabled:
                    # force to skip first option.
                    if row_index > 1:
                        formated_area_list.append(row)

    matched_blocks = []
    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)
        if area_list_count > 0:
            if len(config_dict["date_auto_select"]["date_keyword"]) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", config_dict["date_auto_select"]["date_keyword"])

                matched_blocks = get_matched_blocks_by_keyword(config_dict, config_dict["date_auto_select"]["mode"], config_dict["date_auto_select"]["date_keyword"], formated_area_list)                

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if config_dict["date_auto_select"]["mode"] == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if config_dict["date_auto_select"]["mode"] == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if config_dict["date_auto_select"]["mode"] == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                option_value = ""
                try:
                    option_value = target_area.get_attribute('value')
                except Exception as exc:
                    print("find option value fail")
                    pass
                
                if option_value is None:
                    option_value = ""

                if len(option_value) > 0:
                    # selenium
                    select_obj.select_by_value(option_value);
                    is_date_assign_by_bot = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass


    return is_date_assign_by_bot, is_select_exist

def interpart_time_auto_select(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    if show_debug_message:
        print("time_keyword:", config_dict["time_auto_select"]["time_keyword"])

    is_select_exist = False

    my_css_selector = '#play_time'
    form_select = None
    select_obj = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if form_select is not None:
            select_obj = Select(form_select)
            if not select_obj is None:
                is_select_exist = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    area_list = None
    if is_select_exist:
        try:
            area_list = select_obj.options
        except Exception as exc:
            pass

    is_time_assign_by_bot = False
    if not area_list is None:
        if show_debug_message:
            print("len(area_list):", len(area_list))
        if len(area_list) > 0:
            is_select_exist = True

            if len(area_list) == 1:
                # skip this round wait ajax return.
                area_list = None
            else:
                # normal case.
                option_value = ""
                try:
                    selected_option = select_obj.first_selected_option
                    option_value = selected_option.get_attribute('value')
                except Exception as exc:
                    pass
                if option_value is None:
                    option_value = ""
                if len(option_value) > 0:
                    print("time is selected.")
                    area_list = None
                    is_time_assign_by_bot = True

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                # default is enabled.
                row_is_enabled=True

                if row_is_enabled:
                    # force to skip first option.
                    if row_index > 1:
                        formated_area_list.append(row)

    matched_blocks = []
    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)
        if area_list_count > 0:
            if len(config_dict["time_auto_select"]["time_keyword"]) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", config_dict["time_auto_select"]["time_keyword"])

                matched_blocks = get_matched_blocks_by_keyword(config_dict, config_dict["time_auto_select"]["mode"], config_dict["date_auto_select"]["time_keyword"], formated_area_list)                

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if config_dict["time_auto_select"]["mode"] == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if config_dict["time_auto_select"]["mode"] == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if config_dict["time_auto_select"]["mode"] == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                option_value = ""
                try:
                    option_value = target_area.get_attribute('value')
                except Exception as exc:
                    print("find option value fail")
                    pass
                
                if option_value is None:
                    option_value = ""

                if len(option_value) > 0:
                    # selenium
                    select_obj.select_by_value(option_value);
                    is_time_assign_by_bot = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass


    return is_time_assign_by_bot, is_select_exist

def interpark_login(driver, account, password):
    is_email_sent = assign_text(driver, By.CSS_SELECTOR, '#memEmail', account)
    is_password_sent = False
    if is_email_sent:
        is_password_sent = assign_text(driver, By.CSS_SELECTOR, '#memPass', password, submit=True)
    return is_password_sent

def escape_to_first_tab(driver, main_window_handle):
    try:
        chwd = driver.window_handles
        window_handles_count = len(chwd)
        if window_handles_count == 1:
            driver.switch_to.window(chwd[0])
        if window_handles_count > 1:
            for w in chwd:
                #switch focus to child window
                if (w!=main_window_handle):
                    driver.switch_to.window(w)
                    break
    except Exception as excSwithFail:
        pass

def hide_bookingGuideLayer(driver):
    div_element = None
    try:
        div_element = driver.find_element(By.CSS_SELECTOR,'#bookingGuideLayer')
        if not div_element is None:
            if div_element.is_displayed():
                js = "CloseBookingLayer();"
                driver.set_script_timeout(1)
                driver.execute_script(js)
    except Exception as exc:
        pass

def hide_capchaLayer(driver):
    div_element = None
    try:
        div_element = driver.find_element(By.CSS_SELECTOR,'#capchaLayer')
        if not div_element is None:
            if div_element.is_displayed():
                js = "$('capchaLayer').hide();"
                driver.set_script_timeout(1)
                driver.execute_script(js)
    except Exception as exc:
        pass

def interpark_event_detail(driver, config_dict, url):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_popup_opener_window = False
    if config_dict["date_auto_select"]["enable"]:
        # get iframes
        frames = driver.find_elements(By.CSS_SELECTOR, 'iframe')
        
        is_need_refresh = True

        frame_index = 0
        for f in frames:
            frame_index += 1
            if show_debug_message:
                print("search at frame index:", frame_index)

            try:
                driver.switch_to.frame(f)
            except Exception as exc:
                pass

            hide_bookingGuideLayer(driver)
            hide_capchaLayer(driver)

            is_date_assign_by_bot, is_select_exist = interpart_date_auto_select(driver, config_dict)
            if is_select_exist:
                is_need_refresh = False
            if show_debug_message:
                print("is_date_assign_by_bot:", is_date_assign_by_bot)

            is_time_assign_by_bot = False
            if is_date_assign_by_bot:
                if config_dict["time_auto_select"]["enable"]:
                    is_time_assign_by_bot, is_select_exist = interpart_time_auto_select(driver, config_dict)

            if is_time_assign_by_bot:
                my_css_selector = 'div.btn_Booking > img'
                btn_buy_tickets = None
                try:
                    btn_buy_tickets = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                    if btn_buy_tickets is not None:
                        print("waiting seat info ajax ready...")
                        print("start to popup opener.")
                        act = ActionChains(driver)
                        act.move_to_element(btn_buy_tickets).perform()
                        btn_buy_tickets.click()
                        is_popup_opener_window = True
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

            try:
                driver.switch_to.default_content()
            except Exception as exc:
                pass

            if is_popup_opener_window:
                break

        if not is_popup_opener_window:
            if is_need_refresh:
                try:
                    driver.refresh()
                    time.sleep(0.3)
                except Exception as exc:
                    pass

    if is_popup_opener_window:
        for i in range(20):
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count == 1:
                    print("waiting for popup window...")
                    time.sleep(0.2)
                else:
                    print("new tab is opened.")
                    break
            except Exception as excSwithFail:
                pass
                
    return is_popup_opener_window


def interpart_goto_step2(driver):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    try:
        driver.switch_to.default_content()
    except Exception as exc:
        pass

    is_step_1_on = False
    image_element = None
    try:
        my_css_selector = "div.step > ul > li.fir.s1 > a > img"
        image_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        image_src = image_element.get_attribute('src')
        if "_on.gif" in image_src:
            is_step_1_on = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    is_next_btn_press = False

    if show_debug_message:
        print("is_step_1_on:", is_step_1_on)
    if is_step_1_on:
        btn_next = None
        try:
            my_css_selector = "#LargeNextBtnImage"
            btn_next = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            if not btn_next is None:
                if btn_next.is_enabled():
                    if btn_next.is_displayed():
                        print("goto step 2")
                        act = ActionChains(driver)
                        act.move_to_element(btn_next).perform()
                        time.sleep(0.2)
                        btn_next.click()
                        is_next_btn_press = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    return is_next_btn_press    

def interpark_get_ocr_answer(driver, ocr):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ocr_answer = None
    if not ocr is None:
        img_base64 = None

        image_id = 'imgCaptcha'
        image_element = None
        try:
            my_css_selector = "#" + image_id
            image_element = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if not image_element is None:
            try:
                driver.set_script_timeout(1)
                form_verifyCode_base64 = driver.execute_async_script("""
                    var canvas = document.createElement('canvas');
                    var context = canvas.getContext('2d');
                    var img = document.getElementById('%s');
                    if(img!=null) {
                    canvas.height = img.naturalHeight;
                    canvas.width = img.naturalWidth;
                    context.drawImage(img, 0, 0);
                    callback = arguments[arguments.length - 1];
                    callback(canvas.toDataURL()); }
                    """ % (image_id))
                if not form_verifyCode_base64 is None:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            except Exception as exc:
                if show_debug_message:
                    print("canvas exception:", str(exc))
                pass

        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

    return ocr_answer

def interpark_keyin_captcha_code(driver, form_verifyCode, answer = ""):
    is_form_sumbited = False

    if form_verifyCode is not None:
        is_visible = False
        try:
            if form_verifyCode.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""
            is_visible = False

        if is_visible:
            try:
                form_verifyCode.click()
            except Exception as exc:
                #print(exc)
                pass

            if len(answer) > 0:
                answer = answer.upper()
                try:
                    form_verifyCode.send_keys(answer)
                    form_verifyCode.send_keys(Keys.ENTER)
                    is_form_sumbited = True
                except Exception as exc:
                    print("send_keys ocr answer fail.")
                    #print(exc)
                    pass


    return is_form_sumbited

def interpart_auto_ocr(driver, ocr, previous_answer):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_need_redo_ocr = False
    is_form_sumbited = False

    is_input_box_exist = False

    form_verifyCode = None
    try:
        form_verifyCode = driver.find_element(By.ID, 'txtCaptcha')
        is_input_box_exist = True
    except Exception as exc:
        pass

    if is_input_box_exist:
        print("start to ddddocr")
        if show_debug_message:
            print("previous_answer:", previous_answer)

        ocr_start_time = time.time()
        ocr_answer = interpark_get_ocr_answer(driver, ocr)
        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))

        if ocr_answer is None:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True
            time.sleep(0.1)
        else:
            ocr_answer = ocr_answer.strip()
            print("ocr_answer:", ocr_answer)

            # for now, not able interact with target element.
            if len(ocr_answer)!=6:
                ocr_answer = ocr_answer + ocr_answer + ocr_answer + ocr_answer + ocr_answer + ocr_answer
                ocr_answer = ocr_answer[:6]

            if len(ocr_answer)==6:
                is_form_sumbited = interpark_keyin_captcha_code(driver, form_verifyCode, answer = ocr_answer)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("change to new captcha.")
                    try:
                        js = "fnCapchaRefresh();"
                        driver.set_script_timeout(1)
                        driver.execute_script(js)
                    except Exception as exc:
                        pass
                    time.sleep(0.2)
    else:
        #print("in this iframe, input box not exist, quit ocr...")
        pass

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def interpart_ocr_main(driver, config_dict, ocr):
    previous_answer = None
    for redo_ocr in range(999):
        is_need_redo_ocr, previous_answer, is_form_sumbited = interpart_auto_ocr(driver, ocr, previous_answer)
        if not is_need_redo_ocr:
            break

def interpark_divBookSeat(driver, config_dict, ocr):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_ocr_iframe_travel = False
    div_element = None
    try:
        div_element = driver.find_element(By.CSS_SELECTOR,'#divBookSeat')
        if not div_element is None:
            if div_element.is_enabled():
                if div_element.is_displayed():
                    print("divBookSeat popup")
                    is_ocr_iframe_travel = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    if is_ocr_iframe_travel:
        is_need_refresh = True

        frames = driver.find_elements(By.CSS_SELECTOR, 'iframe')
        frame_index = 0
        for f in frames:
            frame_index += 1
            if show_debug_message:
                print("search at frame index:", frame_index)

            try:
                driver.switch_to.frame(f)
            except Exception as exc:
                pass
            interpart_ocr_main(driver, config_dict, ocr)
            try:
                driver.switch_to.default_content()
            except Exception as exc:
                pass

def interpart_price_seat_count(div_element):
    is_seat_assigned = False
    print("interpart_price_seat_count")
    try:
        if div_element.is_enabled():
            if div_element.is_displayed():
                select_obj = Select(div_element)
                if not select_obj is None:
                    seat_count = 0
                    seat_count_options = select_obj.options
                    if not seat_count_options is None:
                        seat_count = len(seat_count_options)

                    print("seat_count", seat_count)
                    if seat_count > 0:
                        select_obj.select_by_index(seat_count-1)
                        is_seat_assigned = True

    except Exception as exc:
        print(exc)
        pass

    return is_seat_assigned

def interpart_booking_click_small_next_btn(driver):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    is_step_3_submited = False
    btn_next = None
    try:
        btn_next = driver.find_element(By.CSS_SELECTOR,'#SmallNextBtnLink > img')
        if not btn_next is None:
            if btn_next.is_enabled():
                if btn_next.is_displayed():
                    print("goto step 4")

                    act = ActionChains(driver)
                    act.move_to_element(btn_next).perform()

                    btn_next.click()
                    is_step_3_submited = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    return is_step_3_submited

def interpark_assign_seat_count(driver):
    is_seat_assigned = False
    
    div_element_list = None
    try:
        div_element_list = driver.find_elements(By.CSS_SELECTOR,'td > select')
        if not div_element_list is None:
            print("select count:", len(div_element_list))
            if len(div_element_list) > 0:
                for div_element in div_element_list:
                    is_seat_assigned = interpart_price_seat_count(div_element)
                    print("is_seat_assigned:", is_seat_assigned)
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass
    
    return is_seat_assigned


def interpart_price_discount(driver, config_dict):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    try:
        driver.switch_to.default_content()
    except Exception as exc:
        pass

    is_step_3_on = False
    image_element = None
    try:
        my_css_selector = "div.step > ul > li.s3 > a > img"
        image_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        image_src = image_element.get_attribute('src')
        if "_on.gif" in image_src:
            is_step_3_on = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    is_next_btn_press = False

    if show_debug_message:
        print("is_step_3_on:", is_step_3_on)

    is_step_3_submited = False
    if is_step_3_on:
        print("interpart_price_discount")

        iframe_BookStep = None
        try:
            iframe_BookStep = driver.find_element(By.CSS_SELECTOR,'#ifrmBookStep')
            if not iframe_BookStep is None:
                if iframe_BookStep.is_enabled():
                    if iframe_BookStep.is_displayed():
                        try:
                            driver.switch_to.frame(iframe_BookStep)
                        except Exception as exc:
                            pass

                        is_seat_assigned = interpark_assign_seat_count(driver)

                        try:
                            driver.switch_to.default_content()
                        except Exception as exc:
                            pass

                        # press next button.
                        if is_seat_assigned:
                            is_step_3_submited = interpart_booking_click_small_next_btn(driver)

        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    return is_step_3_submited

def interpark_fill_confirmation(driver, config_dict):
    is_MemberName_sent = assign_text(driver, By.CSS_SELECTOR, '#MemberName', config_dict["user_name"])
    is_BirYear_sent = assign_select_by_text(driver, By.CSS_SELECTOR, '#BirYear', config_dict["user_date_of_birth_year"])
    is_BirMonth_sent = assign_select_by_text(driver, By.CSS_SELECTOR, '#BirMonth', config_dict["user_date_of_birth_month"])
    is_BirDay_sent = assign_select_by_text(driver, By.CSS_SELECTOR, '#BirDay', config_dict["user_date_of_birth_day"])
    if len(config_dict["user_email"]) > 0:
        is_Email_sent = assign_text(driver, By.CSS_SELECTOR, '#Email', config_dict["user_email"])
    else:
        is_Email_sent = True
    is_PhoneNo_sent = assign_text(driver, By.CSS_SELECTOR, '#PhoneNo', config_dict["user_phone_number"])
    is_HpNo_sent = assign_text(driver, By.CSS_SELECTOR, '#HpNo', config_dict["user_cell_phone"])

    is_form_all_filled = True
    if not is_MemberName_sent:
        is_form_all_filled = False
    if not is_BirYear_sent:
        is_form_all_filled = False
    if not is_BirMonth_sent:
        is_form_all_filled = False
    if not is_BirDay_sent:
        is_form_all_filled = False
    if not is_Email_sent:
        is_form_all_filled = False
    if not is_PhoneNo_sent:
        is_form_all_filled = False
    if not is_HpNo_sent:
        is_form_all_filled = False
    return is_form_all_filled


def interpark_fill_profile(driver, config_dict):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    try:
        driver.switch_to.default_content()
    except Exception as exc:
        pass

    is_step_4_on = False
    image_element = None
    try:
        my_css_selector = "div.step > ul > li.s4 > a > img"
        image_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        image_src = image_element.get_attribute('src')
        if "_on.gif" in image_src:
            is_step_4_on = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    is_next_btn_press = False

    if show_debug_message:
        print("is_step_4_on:", is_step_4_on)

    is_step_4_submited = False
    if is_step_4_on:
        print("interpark_fill_profile")

        iframe_BookStep = None
        try:
            iframe_BookStep = driver.find_element(By.CSS_SELECTOR,'#ifrmBookStep')
            if not iframe_BookStep is None:
                if iframe_BookStep.is_enabled():
                    if iframe_BookStep.is_displayed():
                        try:
                            driver.switch_to.frame(iframe_BookStep)
                        except Exception as exc:
                            pass

                        is_profile_assigned = interpark_fill_confirmation(driver, config_dict)
                        print("is_profile_assigned:", is_profile_assigned)

                        try:
                            driver.switch_to.default_content()
                        except Exception as exc:
                            pass

                        # press next button.
                        if is_profile_assigned:
                            is_step_4_submited = interpart_booking_click_small_next_btn(driver)

        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    return is_step_4_submited

def interpark_fill_payment_detail(driver, config_dict):
    is_payment_assigned = False
    
    is_radio_selected = False
    if not config_dict["foreign_card"]:
        # korea local credit card.
        # TODO: in future...
        is_radio_selected = True
        pass

    else:
        el_radio = None
        try:
            el_radio = driver.find_element(By.CSS_SELECTOR, "input[type='radio'][value='G1']")
            if not el_radio is None:
                if not el_radio.is_selected():
                    el_radio.click()
                if el_radio.is_selected():
                    is_radio_selected = True
        except Exception as exc:
            pass

    if is_radio_selected:
        is_CreditCard_selected = assign_select_by_text(driver, By.CSS_SELECTOR, '#DiscountCardGlobal', config_dict["credit_card_type"])
        
        if is_CreditCard_selected:
            is_payment_assigned = True
            real_card_number = decryptMe(config_dict["cc_number"])
            if len(real_card_number)>=16:
                is_CardNo1_sent = assign_text(driver, By.CSS_SELECTOR, '#CardNo1', real_card_number[:4])
                is_CardNo2_sent = assign_text(driver, By.CSS_SELECTOR, '#CardNo2', real_card_number[4:8])
                is_CardNo3_sent = assign_text(driver, By.CSS_SELECTOR, '#CardNo3', real_card_number[8:12])
                is_CardNo4_sent = assign_text(driver, By.CSS_SELECTOR, '#CardNo4', real_card_number[12:16])

                is_ValidMonth_sent = assign_select_by_text(driver, By.CSS_SELECTOR, '#ValidMonth', config_dict["cc_exp_month"])
                is_ValidYear_sent = assign_select_by_text(driver, By.CSS_SELECTOR, '#ValidYear', config_dict["cc_exp_year"])

                if not is_CardNo1_sent:
                    is_payment_assigned = False
                if not is_CardNo2_sent:
                    is_payment_assigned = False
                if not is_CardNo3_sent:
                    is_payment_assigned = False
                if not is_CardNo4_sent:
                    is_payment_assigned = False
                if not is_ValidMonth_sent:
                    is_payment_assigned = False
                if not is_ValidMonth_sent:
                    is_payment_assigned = False

    return is_payment_assigned

def interpark_fill_payment(driver, config_dict):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    try:
        driver.switch_to.default_content()
    except Exception as exc:
        pass

    is_step_5_on = False
    image_element = None
    try:
        my_css_selector = "div.step > ul > li.s5 > a > img"
        image_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        image_src = image_element.get_attribute('src')
        if "_on.gif" in image_src:
            is_step_5_on = True
    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    is_next_btn_press = False

    if show_debug_message:
        print("is_step_5_on:", is_step_5_on)

    is_step_5_submited = False
    if is_step_5_on:
        print("interpark_fill_profile")

        iframe_BookStep = None
        try:
            iframe_BookStep = driver.find_element(By.CSS_SELECTOR,'#ifrmBookStep')
            if not iframe_BookStep is None:
                if iframe_BookStep.is_enabled():
                    if iframe_BookStep.is_displayed():
                        try:
                            driver.switch_to.frame(iframe_BookStep)
                        except Exception as exc:
                            pass

                        is_payment_assigned = interpark_fill_payment_detail(driver, config_dict)
                        print("is_profile_assigned:", is_payment_assigned)

                        is_checkbox_checked = check_checkbox(driver, By.CSS_SELECTOR, '#CancelAgree')
                        is_checkbox_checked = check_checkbox(driver, By.CSS_SELECTOR, '#CancelAgree2')

                        try:
                            driver.switch_to.default_content()
                        except Exception as exc:
                            pass

                        # press next button.
                        if is_payment_assigned:
                            is_step_5_submited = interpart_booking_click_small_next_btn(driver)

        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    return is_step_5_submited

def interpart_booking(driver, config_dict, ocr, is_step_1_submited):
    if not is_step_1_submited:
        is_step_1_submited = interpart_goto_step2(driver)

    if is_step_1_submited:
        if config_dict["ocr_captcha"]["enable"]:
            if ocr is None:
                print("ddddocr component is not able to use, you may running in arm environment.")
            else:
                interpark_divBookSeat(driver, config_dict, ocr)
                pass

        is_step_3_submited = interpart_price_discount(driver, config_dict)

        is_step_4_submited = interpark_fill_profile(driver, config_dict)

        is_step_5_submited = interpark_fill_payment(driver, config_dict)

    return is_step_1_submited

def interpark_main(driver, config_dict, url, ocr, interpark_dict):
    escape_to_first_tab(driver, interpark_dict["main_window_handle"])

    if "globalinterpark.com/user/signin" in url:
        interpark_account = config_dict["advanced"]["interpark_account"]
        if len(interpark_account) > 2:
            interpark_login(driver, interpark_account, decryptMe(config_dict["advanced"]["interpark_password"]))

    if "globalinterpark.com/main/main" in url:
        interpark_change_locale(driver, config_dict)

    if "globalinterpark.com/detail/edetail?prdNo=" in url:
        if not interpark_dict["opener_popuped"]:
            interpark_dict["opener_popuped"] = interpark_event_detail(driver, config_dict, url)
    else:
        interpark_dict["opener_popuped"] = False

    if "/Global/Play/Book/BookMain.asp" in url:
        interpark_dict["is_step_1_submited"] = interpart_booking(driver, config_dict, ocr, interpark_dict["is_step_1_submited"])
    else:
        interpark_dict["is_step_1_submited"] = False

    return interpark_dict

def main(args):
    config_dict = get_config_dict(args)

    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict)
    else:
        print("Load config error!")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    interpark_dict = {}
    interpark_dict["opener_popuped"] = False
    interpark_dict["main_window_handle"] = None
    interpark_dict["is_step_1_submited"] = False

    ocr = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
    except Exception as exc:
        print(exc)
        pass

    while True:
        time.sleep(0.05)

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        url, is_quit_bot = get_current_url(driver)
        if is_quit_bot:
            break

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        is_maxbot_paused = False
        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            is_maxbot_paused = True

        if len(url) > 0 :
            if url != last_url:
                print(url)
                write_last_url_to_file(url)
                if is_maxbot_paused:
                    print("MAXBOT Paused.")
            last_url = url

        if is_maxbot_paused:
            time.sleep(0.2)
            continue

        if len(url) > 0 :
            if url != last_url:
                print(url)
            last_url = url

        if "globalinterpark.com" in url:
            if interpark_dict["main_window_handle"] is None:
                interpark_dict["main_window_handle"] = driver.current_window_handle

            interpark_dict = interpark_main(driver, config_dict, url, ocr, interpark_dict)

        # for facebook
        facebook_login_url = 'https://www.facebook.com/login.php?'
        if url[:len(facebook_login_url)]==facebook_login_url:
            facebook_account = config_dict["advanced"]["facebook_account"].strip()
            if len(facebook_account) > 4:
                facebook_login(driver, facebook_account, decryptMe(config_dict["advanced"]["facebook_password"]))

def cli():
    parser = argparse.ArgumentParser(
            description="MaxBot Aggument Parser")

    parser.add_argument("--input",
        help="config file path",
        type=str)

    parser.add_argument("--homepage",
        help="overwrite homepage setting",
        type=str)

    args = parser.parse_args()
    main(args)

if __name__ == "__main__":
    cli()
