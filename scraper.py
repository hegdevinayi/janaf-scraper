import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pyvirtualdisplay import Display


class ScraperError(Exception):
    """Base class to handle errors associated with the `Scraper` class."""
    pass


class Scraper(object):
    """Base class to crawl http://kinetics.nist.gov/janaf/ using selenium webdriver and ChromeDriver."""

    def __init__(self, use_virtual_display=None, virtual_display_params=None, browser_options=None):

        self._url = 'http://kinetics.nist.gov/janaf/'

        self._use_virtual_display = False
        if use_virtual_display:
            self.use_virtual_display = use_virtual_display

        self._virtual_display_params = {}
        if virtual_display_params:
            self.virtual_display_params = virtual_display_params

        self.virtual_display = None
        if self.use_virtual_display:
            self.virtual_display = Display(**self.virtual_display_params)
            self.start_virtual_display()

        self._browser_options = {}
        if browser_options:
            self.browser_options = browser_options

        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)

    @property
    def url(self):
        """String with the URL to parse (http://kinetics.nist.gov/janaf/). Currently cannot be set."""
        return self._url

    @property
    def use_virtual_display(self):
        """Boolean specifying whether to use a virtual display from PyVirtualDisplay or not."""
        return self._use_virtual_display

    @use_virtual_display.setter
    def use_virtual_display(self, use_virtual_display):
        if isinstance(use_virtual_display, str):
            self._use_virtual_display = use_virtual_display.strip().lower()[0] == 't'
        elif isinstance(use_virtual_display, bool):
            self._use_virtual_display = use_virtual_display

    @property
    def virtual_display_params(self):
        """Dictionary of parameters and corresponding values to pass to `pyvirtualdisplay.Display` constructor."""
        return self._virtual_display_params

    @virtual_display_params.setter
    def virtual_display_params(self, virtual_display_params):
        if not isinstance(virtual_display_params, dict):
            error_msg = 'The `virtual_display_params` argument should be a Dictionary'
            raise ScraperError(error_msg)

        self._virtual_display_params = virtual_display_params

    @property
    def browser_options(self):
        """Dictionary of arguments/options and values specifying the capabilities of the ChromeDriver.

        The ChromeOptions class accepts the following arguments (NOTE: only the ones listed below are supported):

        "binary": String specifying the location of the Chrome executable to use.

        "args": List of Strings, each of which is a command-line argument to use when starting Chrome. Each
                command-line argument should itself have the arguments, associated values separated by a "=" sign.
                E.g. ["user-data-dir=/tmp/temp_profile", "start-maximized"]
                (A list of Chrome arguments is here http://peter.sh/experiments/chromium-command-line-switches.)

        "extensions": List of Strings, each specifying a Chrome extension to install on startup.

        "prefs": Dictionary with preferences to be applied to the user profile in use, and the corresponding values.
                 E.g. {"download": {"default_directory": "/home/example/Desktop", "prompt_for_download": False}}
                 See the "Preferences" file in the default user data directory for more options.

        (https://sites.google.com/a/chromium.org/chromedriver/capabilities has a full list. This is FYI,
        and arguments/options not listed above are *not* supported here.
        """
        return self._browser_options

    @browser_options.setter
    def browser_options(self, browser_options):
        if not self.browser_options:
            args = ['user-data-dir=/tmp/temp_driver_profile']
            prefs = {'download': {'default_directory': os.path.join(os.path.abspath(os.getcwd()), 'driver_downloads'),
                                  'prompt_for_download': False}
                     }
            self._browser_options = {'args': args, 'prefs': prefs}

        if not isinstance(browser_options, dict):
            error_msg = 'The `browser_options` argument should be a Dictionary'
            raise ScraperError(error_msg)

        self._browser_options.update(browser_options)

    @property
    def chrome_options(self):
        """`webdriver.ChromeOptions` instance with the specified `self.browser_options`."""
        _chrome_options = webdriver.ChromeOptions()
        if 'binary' in self.browser_options:
            _chrome_options.binary_location = self.browser_options['binary']
        for arg in self.browser_options.get('args', []):
            _chrome_options.add_argument(arg)
        for ext in self.browser_options.get('extensions', []):
            _chrome_options.add_extension(ext)
        if 'prefs' in self.browser_options:
            _chrome_options.add_experimental_option('prefs', self.browser_options['prefs'])
        return _chrome_options

    def start_virtual_display(self):
        """Starts the `self.virtual_display`."""
        self.virtual_display.start()

    def stop_virtual_display(self):
        """Stops the `self.virtual_display`."""
        self.virtual_display.stop()

    def get_landing_page(self):
        """Navigates to the page in `self.url`."""
        self.browser.get(self.url)

    def send_query(self, query):
        """Finds the query box on the page, and sends argument as keys."""
        self.browser.find_element_by_name('query').send_keys(query)

    def select_state(self, state='cr'):
        """Selects "cr" from the "Specify state" drop-down menu."""
        select_menu = Select(self.browser.find_element_by_tag_name('select'))
        select_menu.select_by_visible_text(state)

    def submit_query(self):
        """Submits the form with the query."""
        self.browser.find_element_by_name('query').submit()

    def _parse_all_query_records(self):
        """Parses, using XPATH, all records resulting from the query."""
        records = {}

        all_rows = self.browser.find_elements_by_xpath('//table/tbody/tr')
        header_columns = all_rows[0].find_elements_by_xpath('./th')

        for data_row in all_rows[1:]:
            cas = None
            formula = None
            name = None
            link = None

            data_columns = data_row.find_elements_by_xpath('./td')

            for header_col, data_col in zip(header_columns, data_columns):
                if 'CAS' in header_col.text:
                    cas = data_col.text.strip()
                elif 'Formula' in header_col.text:
                    formula = data_col.text.strip()
                elif 'Name' in header_col.text:
                    name = data_col.text.strip().lower().replace(',', '_').replace(' ', '_')
                elif 'JANAF' in header_col.text:
                    link = data_col.find_element_by_xpath('./a').get_attribute('href').replace('.html', '.txt')

            if name:
                records[name] = {'CAS': cas, 'formula': formula, 'link': link}

        return records

    @property
    def all_query_records(self):
        """Dictionary of data with all records resulting from the query.

        Returns:
            Dictionary with Strings specifying the full name of compounds as keys, and dictionary of data as values.
            The values dictionary has Strings (one of "CAS", "formula", "link") as keys, and corresponding values,
            also String.
            E.g. {"aluminum_oxide__alpha": {"CAS": "1344-28-1",
                                            "formula": "Al2O3",
                                            "link": "http://kinetics.nist.gov/janaf/html/Al-096.txt"},
                  "aluminum_oxide__delta": {"CAS": "1344-28-1",
                                            "formula": "Al2O3",
                                            "link": "http://kinetics.nist.gov/janaf/html/Al-097.txt"},
                  ...
                  }

        """
        return self._parse_all_query_records()

    def terminate_session(self):
        """Quits the browser, stops the virtual display: terminates the session cleanly."""
        self.browser.stop_client()
        self.browser.quit()
        if self.virtual_display:
            self.stop_virtual_display()


