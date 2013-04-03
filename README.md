edX data scripts
================

Scripts for importing and analyzing data dumps from edX, provided to partner universities.

load_data.py: Loads .sql dumps into a local MySQL database. Depends on table_data.txt.
anonymize.py: Removes data that could personally identify students and anonymizes IDs.
