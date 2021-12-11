_note: this code has not been worked on since 2010. Recent commit dates are just the result of a history rewrite_

# How to install, for complete and utter beginners to everything

1. Get [Python 2.7+](http://python.org/download/) Install this first.
2. Get [Skype4Py](http://sourceforge.net/projects/skype4py/)
3. Get [Beautifulsoup 3.0.8.1 +](http://www.crummy.com/software/BeautifulSoup/) (for the web features of the dynamic command module)
4. Get [Simplejson](http://pypi.python.org/pypi/simplejson/) (for the Omegle module)
5. Download the source code for the bot
6. Install 1-4 from above in roughly that order.
7. Make sure you remember to add python to your PATH variable
8. Run the bot with by typing "python joebot2.py" in your console
9. You'll probably see a bunch of errors spewed by various modules, specifically 'quote', 'lastfm'. You can't run these without some aditional set up, so just open the file in data/modules.txt and put # before the lines of all modules giving you trouble.
10. If you want logging, you need to add a folder called "logs" in data. Otherwise, disable the logging module.
11. The bot should now run nicely!

(note, the bot only works on Windows for some reason! I can't figure out why.)

## Credit

This bot was a fork of https://github.com/Katharine/KathBot3 by Katharine Berry. I adapted it for Skype and then built and maintined a suite of modifications and new modules.
