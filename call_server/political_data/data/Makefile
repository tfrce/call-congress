all: us_legislators.csv us_districts.csv us_states.csv

clean:
	rm -rf -- *.csv

us_legislators.csv:
	curl -k "http://unitedstates.sunlightfoundation.com/legislators/legislators.csv" -o "us_legislators.csv"

us_districts.csv:
	curl -k "http://assets.sunlightfoundation.com/data/districts.csv" -o "us_districts.csv"

us_states.csv:
	curl -k "https://raw.githubusercontent.com/spacedogXYZ/us_governors_contact/master/data.csv" -o "us_states.csv"
