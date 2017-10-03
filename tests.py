import unittest
from scraper import Scraper
from table_parser import Parser


class TestScraper(unittest.TestCase):
    """Unit tests for `scraper.Scraper`."""

    def test_Al2O3_scraper(self):
        """Tests whether all 4 records for "Al2O3" are scraped correctly."""

        # Initialize a `scraper.Scraper` instance.
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

        # Verify number of records scraped.
        self.assertEqual(len(query_records), 4)

        # Check if scraped data is OK.
        self.assertIn('aluminum_oxide__kappa', query_records)
        self.assertEqual(query_records['aluminum_oxide__alpha']['CAS'], '1344-28-1')
        self.assertEqual(query_records['aluminum_oxide__delta']['formula'], 'Al2O3')
        self.assertEqual(query_records['aluminum_oxide__gamma']['link'],
                         'http://kinetics.nist.gov/janaf/html/Al-098.txt')

        # Terminate the session cleanly.
        scraper.terminate_session()


class TestParser(unittest.TestCase):
    """Unit tests for `parser.Parser`."""

    def test_Al2O3_alpha_parser(self):
        """Tests whether data for "Aluminum Oxide, Alpha" is parsed correctly."""

        # Initialize a `parser.Parser` instance
        parser = Parser(url='http://kinetics.nist.gov/janaf/html/Al-096.txt')

        # Raw text data as List
        self.assertEqual(parser.raw_txt_data[0].strip().split()[0].decode(), 'Aluminum')

        # Data as List
        self.assertListEqual(parser.parsed_data_as_list[0], parser.HEADERS)
        self.assertListEqual(parser.parsed_data_as_list[1][:5], [0., 0., 0., float('inf'), -10.02])

        # Data as CSV
        self.assertIsInstance(parser.parsed_data_as_csv, str)

        # Data as Dictionary
        self.assertIsInstance(parser.parsed_data_as_dict, dict)
        self.assertAlmostEqual(parser.parsed_data_as_dict['H-H(T_R)'][2], -6.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
