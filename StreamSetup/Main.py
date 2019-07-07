import selenium
from selenium import webdriver

from os.path import abspath
from pathlib2 import Path

cwd = Path(abspath("."))
chromePath = cwd/"StreamSetup"/"chromedriver.exe"

chromeDriver = webdriver.Chrome(executable_path=str(chromePath))
chromeDriver.get("https://www.facebook.com/CenterEvents1/")
elem = chromeDriver.find_element_by_class_name("_7tk-")
print(elem)
"""import webbrowser

webbrowser.open("https://www.facebook.com/CenterEvents1/?ref=bookmarks")
"""