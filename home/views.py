import base64
import json

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from social.apps.django_app.default.models import UserSocialAuth
import twitter

from home.models import Image 

# QUERY_MAX_STATUSES = 3200
QUERY_MAX_STATUSES = 200

class ImageForm(forms.Form):
    file = forms.FileField()

def login(request):
    
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
def home(request):
    
    context = {"request": request}
    return render_to_response('home.html', context, context_instance=RequestContext(request))

@login_required
def tweet(request):

    examples = {}
    examples["twurl"] = "twurl -d 'status=This is a test tweet' /1.1/statuses/update.json"
    examples["python"] = """

import twitter

api = twitter.Api(
    base_url='https://api.twitter.com/1.1',
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET',
    access_token_key='YOUR_ACCESS_KEY',
    access_token_secret='YOUR_ACCESS_SECRET')
    
api.PostUpdates("This is a test tweet")

"""

    status = request.REQUEST.get("status", None)
    
    api = get_twitter(request.user)
    response = None
    
    if status:
        response = api.PostUpdates(status)[0].AsDict()

    context = {'request': request, 'examples': examples, 'response': response }
    return render_to_response('tweet.html', context, context_instance=RequestContext(request))

@login_required
def query(request):
    
    screen_name = request.REQUEST.get("screen_name", None)
    if not screen_name:
        screen_name = request.user.username
    
    examples = {}
    examples["twurl"] = "twurl -d 'screen_name=%s' /1.1/statuses/home_timeline.json" % (screen_name)
    examples["python"] = """

import twitter

api = twitter.Api(
    base_url='https://api.twitter.com/1.1',
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET',
    access_token_key='YOUR_ACCESS_KEY',
    access_token_secret='YOUR_ACCESS_SECRET')
    
statuses = api.GetUserTimeline(screen_name='%s', count=200)

""" % (screen_name)
    
    api = get_twitter(request.user)
        
    statuses = []  
    max_id = None   
    while True and QUERY_MAX_STATUSES > 0:
         
        # get latest page
        new_statuses = api.GetUserTimeline(screen_name=screen_name, count=200, max_id=max_id)
 
        # out of statuses: done
        if len(new_statuses) == 0:
            break
 
        max_id = min([s.id for s in new_statuses]) - 1
        statuses = statuses + new_statuses
         
        # reached max: done
        if len(statuses) >= QUERY_MAX_STATUSES:
            break

    context = {'request': request, 'examples': examples, 'statuses': statuses}
    return render_to_response('query.html', context, context_instance=RequestContext(request))

@login_required
def media(request):
    
    examples = {}
    examples["twurl"] = "Coming soon..."
    examples["python"] = """

import twitter

api = twitter.Api(
    base_url='https://api.twitter.com/1.1',
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET',
    access_token_key='YOUR_ACCESS_KEY',
    access_token_secret='YOUR_ACCESS_SECRET')
    
url = '%s/media/upload.json' % api.upload_url

data = {}
data['media'] = open(str("/path/to/file"), 'rb').read()

response = api._RequestUrl(url, 'POST', data=data)

"""
    
    api = get_twitter(request.user)
    response = {}
        
    status = request.REQUEST.get("status", None)
    media_type = request.REQUEST.get("media_type", None)

    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        
        # save to file
        image = Image(file = file)
        image.save()
        
        url = '%s/media/upload.json' % api.upload_url
        
        contents = open(str(image.file.path), 'rb').read()
        data = {}
        
        if media_type == "binary":
            
            # using 'media' parameter (binary)
            data['media'] = contents

        else:
            
            # using 'media_data' parameter (base64)
            import base64
            contents = base64.b64encode(contents)
            data['media_data'] = contents
        
        json_data = api._RequestUrl(url, 'POST', data=data)
        response['media'] = json.loads(json_data.content)
        
        if not 'error' in response['media'] and not 'errors' in response['media']:
            
            response_media = api._ParseAndCheckTwitter(json_data.content)
            response['media'] = response_media
            
            media_id = response_media['media_id_string']
            
            data = {'status': status, 'media_ids': [media_id]}
    
            url = '%s/statuses/update.json' % api.base_url
    
            json_data = api._RequestUrl(url, 'POST', data=data)
            data = api._ParseAndCheckTwitter(json_data.content)
            response['tweet'] = data

    context = {'request': request, 'examples': examples, 'form': form, 'response': response}
    return render_to_response('media.html', context, context_instance=RequestContext(request))

@login_required
def profile(request):
    
    examples = {}
    examples["twurl"] = "Coming soon..."
    examples["python"] = """

import twitter

api = twitter.Api(
    base_url='https://api.twitter.com/1.1',
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET',
    access_token_key='YOUR_ACCESS_KEY',
    access_token_secret='YOUR_ACCESS_SECRET')
    
api.UpdateImage("/path/to/file")

"""
    
    api = get_twitter(request.user)
    response = None
        
    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        
        # save to file
        image = Image(file = file)
        image.save()
        
        response = api.UpdateImage(image.file.path)
        
    context = {'request': request, 'examples': examples, 'form': form, 'response': response}
    return render_to_response('profile.html', context, context_instance=RequestContext(request))

from django.contrib.auth import logout as auth_logout
def logout(request):
    
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')

def get_twitter(user):

    consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY  
    consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET 
    access_token_key = settings.TWITTER_ACCESS_TOKEN 
    access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET 

    usa = UserSocialAuth.objects.get(user=user, provider='twitter')
    if usa:
        access_token = usa.extra_data['access_token']
        if access_token:
            access_token_key = access_token['oauth_token']
            access_token_secret = access_token['oauth_token_secret']

    if not access_token_key or not access_token_secret:
        raise Exception('No user for twitter API call')

    api = twitter.Api(
        base_url='https://api.twitter.com/1.1',
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token_key,
        access_token_secret=access_token_secret)

    return api