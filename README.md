nose-excel
==========
Nose Plugin for Excel report

Usage
=====
Added to nosetests next parameters:
```bash
$ nosetests -h
...
  --with-excel          Enable plugin Excel: This plugin provides test results
                        in the standard Excel XLS file. [NOSE_WITH_EXCEL]
  --excel-file=FILE     Path to xls file to store the excel report in. Default
                        is nosetests.xls in the working directory
                        [NOSE_EXCEL_FILE]
  --excel-testsuite-name=PACKAGE
                        Name of the testsuite in the xls, generated by plugin.
                        Default test suite name is nosetests.
...
```
