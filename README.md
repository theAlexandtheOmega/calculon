# calculon
dependencies: 
sqlobject
discord
django (deprecated soon)
mysqlclient

all are avail through pip3

other dependencies: 
mysql 


setup steps:
create a mysql database for your calculon instance
copy the sqlsettings.py~example file to sqlsettings.py
replace the database info with the login info for your sql db
copy the tokens.py~example to tokens.py
replace the indicated text with your bot token

run the following cmd from your terminal: 
python3 calculonDB.py

this will build your database tables. 

make sure that either the project home folder is in your PYTHONPATH or you're running the 
bot from a command executed in the directory. 

replace the id on this line of calculon.py with your: 


to run the bot:
python3 calculon.py





