import unittest
from crawler import Crawler


class TestCrawler(unittest.TestCase):
    """Unit tests for `crawler.Crawler`."""

    def test_crawler(self):
        crawler = Crawler()
        crawler.get_page()

        # Is the landing page correct?
        self.assertIn('NIST-JANAF Thermochemical Tables', crawler.browser.title)

        crawler.terminate_session()


if __name__ == '__main__':
    unittest.main()
