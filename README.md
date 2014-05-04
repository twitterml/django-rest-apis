sample-django-app
=================

Sample Django App for Twitter using OAuth

REQUIREMENTS
============

To run this sample code, you'll need to install the following libraries:

- Python Social Auth (https://github.com/omab/python-social-auth)
- Python Twitter (https://github.com/bear/python-twitter)
- south (http://south.aeracode.org/)
- Fabric (http://www.fabfile.org/)

GETTING STARTED
============

- Create a Twitter App (https://apps.twitter.com/)
- Specify your Twitter App tokens in app/settings.py under the following section:

  SOCIAL_AUTH_TWITTER_KEY = 'YOUR_TWITTER_KEY'
  SOCIAL_AUTH_TWITTER_SECRET = 'YOUR_TWITTER_SECRET'

- To initialize your database, run the from the `sample-djang-app` directory:

  python manage.py syncdb

- To start the server, run the following from the `sample-djang-app` directory:

  fab start
  
- Open a browser and go to http://localhost:9000