Twitter REST APIs with Django
=================

Sample Django App using Twitter OAuth and REST APIs

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

Requirements
============

To run this sample code, you'll need to install the following libraries:

- Python Social Auth (https://github.com/omab/python-social-auth)
- Python Twitter (https://github.com/bear/python-twitter)
- south (http://south.aeracode.org/)
- Fabric (http://www.fabfile.org/)

Getting Started
============

- Create a Twitter App (https://apps.twitter.com/)
- Specify your Twitter App tokens in app/settings.py under the following section:

    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''

- To initialize your database, run the from the `sample-djang-app` directory:

  python manage.py syncdb

- To start the server, run the following from the `sample-djang-app` directory:

  fab start
  
- Open a browser and go to http://localhost:9000

Deploying to Heroku
============

Deploying to Heroku is even easier. 

- Click on the Heroku button below
- When prompted during the Heroku install, specify your:

	- CONSUMER_KEY
	- CONSUMER_SECRET
	- ACCESS_TOKEN
	- ACCESS_TOKEN_SECRET

- Open a browser and go to the URL specified by your deploy

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

NOTES
============
If you receive a 401 at login/twitter it is most likely caused by a datetime discrepancy between the server making the requst and the Twitter server.

Use NTP to sync time on your server to compensate for the dift.

If you are getting this error on OSX, toggle the "set time zone" checkbox off and back on in Date & Time system preferences for a manual and temporary fix. It has been reported that OSX 10.9 Mavericks has an issue with time drift.

