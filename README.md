# README #

### What is this repository for? ###

This repository stores a utility created for simplifying generating custom Redmine reports.
Uses Python 3.5+, python-redmine and reportlab Python extension modules.

### How do I get set up? ###

Install requirements.txt. To get started, a valid Redmine URL and an API key must be specified in settings.py.
The utility has no GUI, simply run main.py with no arguments to generate a report:

```python main.py```

settings.py contains all needed information.
You can create and use local_settings.py for development, which has a higher priority when importing.

Other customizable settings include language, time period, activity override preferences, etc.

[More info on Redmine REST API](http://www.redmine.org/projects/redmine/wiki/Rest_api)

### Who do I talk to? ###

julia.nikolaeva@live.com