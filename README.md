Twitter REST APIs with Django
=================

Sample Django App using Twitter OAuth and REST APIs

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/twitterdev/django-rest-apis)

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

- In the Twitter App config, ensure the Callback URL is `http://127.0.0.1:9000/complete/twitter`

- Specify your Twitter App tokens in app/settings.py:

    SOCIAL_AUTH_TWITTER_KEY = ''
    
    SOCIAL_AUTH_TWITTER_SECRET = ''
    
    TWITTER_ACCESS_TOKEN = ''
    
    TWITTER_ACCESS_TOKEN_SECRET = ''

- To initialize your database, run the from the `django-rest-apis` directory:

  `python manage.py syncdb`

- To start the server, run the following from the `django-rest-apis` directory:

  `fab start`
  
- Open a browser and go to http://127.0.0.1:9000

Deploying to Heroku
============

Deploying to Heroku is even easier.  

- Create a Twitter App (https://apps.twitter.com/)
- Click on the Heroku button below
- When prompted during the Heroku install, specify your:

	- CONSUMER_KEY
	- CONSUMER_SECRET
	- ACCESS_TOKEN
	- ACCESS_TOKEN_SECRET
	
- After deploying, in the Twitter App config, ensure the Callback URL is `http://your-app-name.herokuapp.com/complete/twitter`

- Open a browser and go to the URL specified by your deploy (http://your-app-name.herokuapp.com)

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/twitterdev/django-rest-apis)


NOTES
============
If you receive a 401 at login/twitter it is most likely caused by a datetime discrepancy between the server making the requst and the Twitter server.

Use NTP to sync time on your server to compensate for the dift.

If you are getting this error on OSX, toggle the "set time zone" checkbox off and back on in Date & Time system preferences for a manual and temporary fix. It has been reported that OSX 10.9 Mavericks has an issue with time drift.

