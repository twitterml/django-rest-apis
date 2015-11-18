Twitter Sign In and REST APIs
=================

Sample Django App using Twitter Sign in (OAuth) and REST APIs. This is the basis for many
types of campaigns, including:

- Capture @username via Twitter Login
- Contest/sweepstakes sign-up via Twitter
- Tweet out a photo from a user (requires user's explicit consent)
- Induce interests via friends & followers 

<img src="screenshot.png" style="width: 70%;"/>

As always, when developing on top of the Twitter platform, you must abide by the [Developer Agreement & Policy](https://dev.twitter.com/overview/terms/agreement-and-policy). 

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/twitterdev/twitter-signin-and-apis)

Requirements
============

To run this sample code, you'll need to install the following libraries:

- Python Social Auth (https://github.com/omab/python-social-auth)
- Python Twitter (https://github.com/bear/python-twitter)
- south (http://south.aeracode.org/)
- Fabric (http://www.fabfile.org/)

You can install these with the following command:

    pip install -r requirements.txt

Getting Started
============

- Create a Twitter App (https://apps.twitter.com/)

- In the Twitter App config, ensure the Callback URL is `http://127.0.0.1:9000/complete/twitter`

- Specify your database settings in app/settings.py. Be sure to uncomment the section for using a local database.
  (The default is set to easily deploy to Heroku.) 

- Specify your Twitter App tokens in app/settings.py:

    SOCIAL_AUTH_TWITTER_KEY = ''
    
    SOCIAL_AUTH_TWITTER_SECRET = ''
    
    TWITTER_ACCESS_TOKEN = ''
    
    TWITTER_ACCESS_TOKEN_SECRET = ''

- To initialize your database, run the from the `twitter-signin-and-apis` directory:

  `python manage.py syncdb`

- To start the server, run the following from the `twitter-signin-and-apis` directory:

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

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/twitterdev/twitter-signin-and-apis)


NOTES
============
If you receive a 401 at login/twitter it is most likely caused by a datetime discrepancy between the server making the requst and the Twitter server.

Use NTP to sync time on your server to compensate for the dift.

If you are getting this error on OSX, toggle the "set time zone" checkbox off and back on in Date & Time system preferences for a manual and temporary fix. It has been reported that OSX 10.9 Mavericks has an issue with time drift.

