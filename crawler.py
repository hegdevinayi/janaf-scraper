import os
from selenium import webdriver
from pyvirtualdisplay import Display


class JanafCrawler(object):
    """Base class to crawl http://kinetics.nist.gov/janaf/ using the selenium webdriver."""

    def __init__(self, display_size=None, display_visible=None, browser_data_dir=None, default_download_dir=None):

        self._url = 'http://kinetics.nist.gov/janaf/'

        self._display_size = None
        self.display_size = display_size

        self._display_visible = None
        self.display_visible = display_visible

        self._browser_data_dir = None
        self.browser_data_dir = browser_data_dir

        self._default_download_dir = None
        self.default_download_dir = default_download_dir

    @property
    def url(self):
        """String with the URL to parse (http://kinetics.nist.gov/janaf/). Currently cannot be set."""
        return self._url

    @property
    def display_size(self):
        """Tuple with the width and height of the virtual diplay."""
        return self._display_size

    @display_size.setter
    def display_size(self, display_size):
        self._display_size = (1024, 768)
        if display_size is not None:
            self._display_size = display_size

    @property
    def display_visible(self):
        """Boolean specifying if the virtual display should be visible or not."""
        return self._display_visible

    @display_visible.setter
    def display_visible(self, display_visible):
        self._display_visible = False
        if display_visible is not None:
            if isinstance(display_visible, str):
                self._display_visible = display_visible.strip().lower()[0] == 't'
            elif isinstance(display_visible, bool):
                self._display_visible = display_visible

    @property
    def browser_data_dir(self):
        """String with the location of the folder containing webdriver data."""
        _browser_data_dir = os.path.join(os.path.abspath(os.getcwd()), 'browser_data')
        return _browser_data_dir

    @browser_data_dir.setter
    def browser_data_dir(self, browser_data_dir):
        self._browser_data_dir = os.path.join(os.path.abspath(os.getcwd()), 'browser_data')
        if browser_data_dir is not None:
            if os.path.isdir(browser_data_dir):
                self._browser_data_dir = os.path.abspath(browser_data_dir)
            else:
                error_msg = 'Input browser data directory {} does not exist'.format(browser_data_dir)
                raise FileNotFoundError(error_msg)

    @property
    def default_download_dir(self):
        """String with the absolute path of the location to save downloaded data by default."""
        return self._default_download_dir

    @default_download_dir.setter
    def default_download_dir(self, default_download_dir):
        self._default_download_dir = os.path.join(self.browser_data_dir, 'driver_downloads')
        if default_download_dir is not None:
            if os.path.isdir(default_download_dir):
                self._default_download_dir = os.path.abspath(default_download_dir)
            else:
                error_msg = 'Input default download directory {} does not exist'.format(default_download_dir)
                raise FileNotFoundError(error_msg)

    @property
    def virtual_display(self):
        """A pyvirtualdisplay.Display object with the specified visibility and size."""
        return Display(visible=self.display_visible, size=self.display_size)




