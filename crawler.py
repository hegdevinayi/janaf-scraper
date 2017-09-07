import os
from selenium import webdriver
from pyvirtualdisplay import Display


class CrawlerError(Exception):
    """Base class to handle errors associated with the `Crawler` class."""
    pass


class Crawler(object):
    """Base class to crawl http://kinetics.nist.gov/janaf/ using selenium webdriver and ChromeDriver."""

    def __init__(self, display_params=None, browser_options=None):

        self._url = 'http://kinetics.nist.gov/janaf/'

        self._display_params = {}
        if display_params:
            self.display_params = display_params

        self.virtual_display = Display(**self.display_params)
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
    def display_params(self):
        """Dictionary of parameters and corresponding values to pass to `pyvirtualdisplay.Display` constructor."""
        return self._display_params

    @display_params.setter
    def display_params(self, display_params):
        if not isinstance(display_params, dict):
            error_msg = 'The `display_params` argument should be a Dictionary'
            raise CrawlerError(error_msg)

        self._display_params = display_params

    @property
    def browser_options(self):
        """Dictionary of arguments/options and values specifying the capabilities of the ChromeDriver.

        The ChromeOptions class accepts the following arguments (NOTE: only the ones listed below are supported):

        "binary": String specifying the location of the Chrome executable to use.

        "args": List of Strings, each of which is a command-line argument to use when starting Chrome. Each
                command-line argument should itself have the arguments, associated values separated by a "=" sign. A
                list of Chrome arguments is here http://peter.sh/experiments/chromium-command-line-switches.
                E.g. ["user-data-dir=/tmp/temp_profile", "start-maximized"]

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
            raise CrawlerError(error_msg)

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
        if "prefs" in self.browser_options:
            _chrome_options.add_experimental_option('prefs', self.browser_options['prefs'])
        return _chrome_options

    def start_virtual_display(self):
        """Starts the `self.virtual_display`."""
        self.virtual_display.start()

    def stop_virtual_display(self):
        """Stops the `self.virtual_display`."""
        self.virtual_display.stop()

    def get_page(self):
        """The HTTP GET method to navigate to a page."""
        self.browser.get(self.url)

    def terminate_session(self):
        """Quit the browser, stop the virtual display: terminate the session cleanly."""
        self.browser.stop_client()
        self.browser.quit()
        self.stop_virtual_display()


