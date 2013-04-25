edX data scripts
================

Scripts for importing and analyzing data dumps from edX, provided to partner universities.

load_data.py: Loads .sql dumps into a local MySQL database. Depends on table_data.txt.
load_mongo.py: Loads .mongo dumps into a local MongoDB database.
anonymize.py: Removes data from MySQL database that could personally identify students
              and anonymizes IDs.
filter_tracking.py: Example script to read and filter the JSON records from the clickstream/
                    click-tracking logs. Designed to read from a compressed 7-Zip archive.
