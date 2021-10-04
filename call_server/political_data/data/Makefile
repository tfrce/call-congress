all: legislators-current.yaml us_districts.csv us_states.csv

clean:
	rm -rf -- *.csv *.yaml

legislators-current.yaml :
	curl -k "https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-current.yaml" -o "legislators-current.yaml"

us_districts.csv:
	curl -k "https://raw.githubusercontent.com/OpenSourceActivismTech/us_zipcodes_congress/master/zccd.csv" -o "us_districts.csv"

us_states.csv:
	curl -k "https://raw.githubusercontent.com/spacedogXYZ/us_governors_contact/master/data.csv" -o "us_states.csv"
