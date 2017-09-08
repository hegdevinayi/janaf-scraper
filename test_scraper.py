import unittest
from scraper import Scraper


class TestScraper(unittest.TestCase):
    """Unit tests for `scraper.Scraper`."""

    def test_Al2O3_scraper(self):
        scraper = Scraper()
        scraper.get_landing_page()

        # Is the landing page correct?
        self.assertIn('NIST-JANAF Thermochemical Tables', scraper.browser.title)

        # Enter "Al2O3" in the form, submit it.
        scraper.send_query('Al2O3')
        scraper.select_state()
        scraper.submit_query()

        # Get all records resulting from the above query
        query_records = scraper.all_query_records
        # Number of records scraped.
        self.assertEqual(len(query_records), 4)
        # Check is scraped data is OK.
        self.assertIn('aluminum_oxide__kappa', query_records)
        self.assertEqual(query_records['aluminum_oxide__alpha']['CAS'], '1344-28-1')
        self.assertEqual(query_records['aluminum_oxide__delta']['formula'], 'Al2O3')
        self.assertEqual(query_records['aluminum_oxide__gamma']['link'],
                         'http://kinetics.nist.gov/janaf/html/Al-098.txt')

        # Terminate the session cleanly.
        scraper.terminate_session()


if __name__ == '__main__':
    unittest.main()
