import logging
from logging import debug

if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG,
		format= '%(asctime)s - %(levelname)s - %(message)s')

import webbrowser
debug("Opening Youtube Livestreaming")
webbrowser.open("https://www.youtube.com/livestreaming/")
