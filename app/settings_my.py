try:
    from app.settings import *
except ImportError, exp:
    pass

DEBUG = True

# Uncomment for local database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SOCIAL_AUTH_TWITTER_KEY = 'N2hofawqPbllo3xMPkvmdNmp6'
SOCIAL_AUTH_TWITTER_SECRET = 'fOnPds7zioGgFqa6ZWsSFtusbqk2w7lW0V0OKicZnCTW2ARsqh'

TWITTER_ACCESS_TOKEN = '987121-b2aHZyd8XID6hJ0kqHxwMLPDPa7yPstNvjnohFNBAwR'
TWITTER_ACCESS_TOKEN_SECRET = 'eNTm9WLC1JITTMsUBEbWY5uMeugqXOEcYb3pnAibgARWT'

