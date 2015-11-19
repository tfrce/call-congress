all: us_legislators.csv us_districts.csv

clean:
	rm -rf -- *.csv

us_legislators.csv:
	curl -k "http://unitedstates.sunlightfoundation.com/legislators/legislators.csv" -o "us_legislators.csv"

us_districts.csv:
	curl -k "http://assets.sunlightfoundation.com/data/districts.csv" -o "us_districts.csv"

us_states.csv:
	curl -k "https://morph.io/spacedogXYZ/50_states_data/data.csv?key=YgVMV7rh4ZvcTriaeNXX&query=select+%2A+from+%27data%27" -o "us_states.csv"