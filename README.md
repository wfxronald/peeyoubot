# peeyoubot: Pump It Up Clears Tracker

<img src="https://cdn3.iconfinder.com/data/icons/popular-services-brands-vol-2/512/telegram-512.png" alt="Telegram Logo" width="15%">

A telegram bot designed to keep track of the clears in the game Pump It Up. More information can be found on the website http://peeyoubot.herokuapp.com/. The bot obtains most of the information through the PumpOut API, a database containing the most recent Pump It Up songs and charts: https://pumpout2020.anyhowstep.com/

The bot uses FuzzyWuzzy library for string detection to intelligently deduce the actual song and chart from the input that the user gives. The bot will then store the user data on Heroku PostgreSQL database, and this same database is used to generate a tier-list in the project peeyouweb: https://github.com/wfxronald/peeyouweb

## Skills learnt
- REST API
- Python Flask
- Telegram Bot Development
- PostgreSQL Integration with SQLAlchemy
- Heroku Deployment
