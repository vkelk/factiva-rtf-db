# coding=utf-8

"""
  https://sraf.nd.edu
  Bill McDonald 2017

  This module provides a class module for the data input from LM_10X_Summaries_YYYY.csv.
  The module takes as input a string which is a line from the data file.
  Be sure to consume the header line in your loop reading the file.
  Each line is converted into the variables contained in the file.
  The __main__ section below provides a simple example of usage.

"""

import time


class cl_LM10XSummaries:
    def __init__(self, _line, missing_values=''):

        parts = _line.strip("\n").split(",")
        self.cik = converter(parts[0], "int", missing_values)
        self.filing_date = converter(parts[1], "int", missing_values)
        self.fiscal_year_end = converter(parts[2], "int", missing_values)
        self.form_type = converter(parts[3], "string", missing_values)
        self.file_name = converter(parts[4], "string", missing_values)
        self.sic = converter(parts[5], "int", missing_values)
        self.ffind = converter(parts[6], "int", missing_values)
        self.n_words = converter(parts[7], "int", missing_values)
        self.n_unique = converter(parts[8], "int", missing_values)
        self.n_negative = converter(parts[9], "int", missing_values)
        self.n_positive = converter(parts[10], "int", missing_values)
        self.n_uncertain = converter(parts[11], "int", missing_values)
        self.n_litigious = converter(parts[12], "int", missing_values)
        self.n_modalweak = converter(parts[13], "int", missing_values)
        self.n_modalmoderate = converter(parts[14], "int", missing_values)
        self.n_modalstrong = converter(parts[15], "int", missing_values)
        self.n_constraining = converter(parts[16], "int", missing_values)
        self.n_negation = converter(parts[17], "int", missing_values)
        self.grossfilesize = converter(parts[18], "int", missing_values)
        self.netfilesize = converter(parts[19], "int", missing_values)
        self.ascii_encoded_chars = converter(parts[20], "int", missing_values)
        self.html_chars = converter(parts[21], "int", missing_values)
        self.xbrl_chars = converter(parts[22], "int", missing_values)
        self.xml_chars = converter(parts[23], "int", missing_values)
        self.n_tables = converter(parts[24], "int", missing_values)
        self.n_exhibits = converter(parts[25], "int", missing_values)

        return


def converter(_var, _ctype, missing_values):
    # missing_values should be passed as a string variable
    _attr = missing_values
    if _ctype != 'int' and _ctype != 'float' and _ctype != 'string':
        print('\n\nERROR in converter: _ctype = {0}'.format(_ctype))
        quit()
    if _ctype == 'int':
        if _var:
            _attr = int(_var)
        else:
            try:
                _attr = int(missing_values)
            except TypeError:
                return _attr
    elif _ctype == 'float':
        if _var:
            _attr = float(_var)
        else:
            try:
                _attr = float(missing_values)
            except TypeError:
                return _attr
    elif _ctype == 'string':
        if _var:
            _attr = _var
        else:
            try:
                _attr = str(missing_values)
            except TypeError:
                return _attr

    return _attr


if __name__ == '__main__':
    print('\n{0}\nPROGRAM NAME:Class_LM10XSummaries.py'.format(time.strftime('%c')))
    source_file = "D:/GD/EDGAR/ParsedData/LM_10X_Summaries_2016.csv"
    f_in = open(source_file)
    header = f_in.readline()  # Consume header line
    n_test = 10
    n = 0
    for line in f_in:
        lm_sum = cl_LM10XSummaries(line, missing_values="")
        print(lm_sum.__dict__)
        # Sample calculation
        bad = (lm_sum.n_negative + lm_sum.n_modalweak) / lm_sum.n_words
        doc_structure = (lm_sum.html_chars + lm_sum.xbrl_chars + lm_sum.xml_chars) / lm_sum.netfilesize
        n += 1
        if n > 10:
            break

    print('\n\nNormal termination.\n{0}\n'.format(time.strftime('%c')))





