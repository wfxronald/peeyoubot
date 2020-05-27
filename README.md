# peeyoubot: Pump It Up Clears Tracker

<img src="https://cdn3.iconfinder.com/data/icons/popular-services-brands-vol-2/512/telegram-512.png" alt="Telegram Logo" width="15%">

A telegram bot designed to keep track of the clears in the game Pump It Up. More information can be found on the <a href="http://peeyoubot.herokuapp.com/">website</a>. The bot obtains most of the information from the <a href="https://pumpout2020.anyhowstep.com/">PumpOut</a> API, a database containing the most recent Pump It Up songs and charts

The bot uses <a href="https://github.com/seatgeek/fuzzywuzzy">FuzzyWuzzy</a> library in Python for string detection to intelligently deduce the actual song and chart from the input that the user gives. The bot will then store the user data on Heroku PostgreSQL database, and this same database is used to generate a tier-list in the project <a href="https://github.com/wfxronald/peeyouweb">peeyouweb</a> 

## Skills learnt
- REST API
- Python Flask
- Telegram Bot Development
- PostgreSQL Integration with SQLAlchemy
- Heroku Deployment
