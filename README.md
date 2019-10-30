## Getting started

- Run `bash ./install_packages.sh `.
- If running Python 3.6 on OS X you will need to run the command `/Applications/Python\ 3.6/Install\ Certificates.command` to allow SSL certification.
- Run `python scrapeProfiles.py URLs.txt`.
- If using Chrome browser, [install chromedriver](http://chromedriver.chromium.org/downloads) and have the driver set to `webdriver.Chrome(executable_path=chromedriver_location)`. If using Firefox, [install geckodriver.exe](https://github.com/mozilla/geckodriver/releases/tag/v0.24.0) and set driver to `webdriver.Firefox(executable_path=geckodriver.exe_location)`. Move the drivers to the drivers subfolder. Example: `driver = webdriver.Chrome(r"drivers/chromedriver")` 



## Contributors

- Arjun Soin
- Jeffrey Naecker
- Daniel Bjorkegren
- Kevin Koech

