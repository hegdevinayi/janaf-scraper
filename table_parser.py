import urllib.request


class ParserError(Exception):
    """Base class to handle errors associated with parsing NIST-JANAF tables."""
    pass


class Parser(object):
    """Base class to parse NIST-JANAF tables."""

    def __init__(self, url=None):
        """Constructor.

        Args:
            url: String with the URL of the NIST-JANF data to be parsed. Defaults to None.
                 E.g. "http://kinetics.nist.gov/janaf/html/Al-096.txt"

        """

        self.HEADERS = ['T', 'C_p', 'S', '-[G-H(T_R)]/T', 'H-H(T_R)', 'dHf', 'dG', 'log_K_f']

        self._url = None
        if url:
            self.url = url

        self._raw_txt_data = self._get_raw_txt_data()

    @property
    def url(self):
        """String specifying the URL of a NIST-JANAF table in plain text."""
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def raw_txt_data(self):
        """List with raw NIST-JANAF table data from `self.url`. (EOL used to split the data into lists.)"""
        return self._raw_txt_data

    def _parse_raw_table(self, raw_table):
        parsed_data = []
        parsed_data.append(self.HEADERS)
        for raw_row in raw_table:
            parsed_data.append(self._parse_raw_row(raw_row))
        return parsed_data

    def _parse_raw_row(self, raw_row):
        parsed_row = []

        split_row = raw_row.decode().strip().split()
        if len(split_row) != len(self.HEADERS):
            return parsed_row

        for column in split_row:
            if 'INFI' in column:
                parsed_row.append(float('inf'))
                continue

            try:
                parsed_row.append(float(column))
            except ValueError:
                parsed_row.append(float('nan'))

        return parsed_row

    def _get_raw_txt_data(self):
        if not self.url:
            return
        with urllib.request.urlopen(url=self.url) as ftxt:
            return ftxt.readlines()

    @property
    def parsed_data_as_list(self):
        """List (of Lists) with the parsed NIST-JANAF data.

        The first List is the header list, i.e., with Strings specifying the column headers `self.HEADERS`. Rest of
        the Lists contain Floating point numbers representing data corresponding to the column headers.
        Missing values or those that were not parsed successfully are Float('nan')/NaN.

        """
        return self.parse_raw_txt_data()

    def parse_raw_txt_data(self):
        """Parses `self.raw_txt_data` into a List of Lists of Float."""
        if not self.raw_txt_data:
            return
        return self._parse_raw_table(self.raw_txt_data[2:])

    @property
    def parsed_data_as_csv(self):
        """String with the parsed NIST-JANAF data in the generalized-CSV format."""
        return self.parsed_data_to_csv()

    def parsed_data_to_csv(self, separator=','):
        """Converts the parsed NIST-JANAF data into the CSV format.

        Args:
            separator: Character to be used to separate column data in the CSV format.

        Returns: String with the parsed NIST-JANAF data in the generalized-CSV format.

        """
        if not self.parsed_data_as_list:
            return
        return '\n'.join([separator.join(map(str, row)) for row in self.parsed_data_as_list])

    @property
    def parsed_data_as_dict(self):
        """Dictionary with the parsed NIST-JANAF data.

        Keys of the dictionary are Strings with the column header from `self.HEADER` and values are Lists of
        Floating point numbers.
        """
        data_dict = dict([(header, []) for header in self.HEADERS])
        for row in self.parsed_data_as_list[1:]:
            for index in range(len(row)):
                data_dict[self.HEADERS[index]].append(row[index])
        return data_dict

