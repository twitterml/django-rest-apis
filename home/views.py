import base64
import json

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from social.apps.django_app.default.models import UserSocialAuth

import twitter
from twitter import TwitterError

from home.models import Image 

# QUERY_MAX_STATUSES = 3200
QUERY_MAX_STATUSES = 200

SIZE_5MB = 5 * 1024 * 1024

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
def media_photo(request):

    examples = {}
    examples["twurl"] = "twurl -H upload.twitter.com \"/1.1/media/upload.json\" -f /path/to/file -F media -X POST"
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
    return media(request, "photo", examples, 'media_photo.html')

@login_required
def media_video(request):

    examples = {}
    examples["twurl"] = """

split -b 5m video_launch.mp4

twurl -H upload.twitter.com "/1.1/media/upload.json" -d "command=INIT&media_type=video/mp4&total_bytes=6634737" 

{"media_id":601491637433475073,"media_id_string":"601491637433475073","expires_after_secs":3599}

twurl -H upload.twitter.com "/1.1/media/upload.json" -d "command=APPEND&media_id=601491637433475073&segment_index=0" --file ./xaa --file-field "media"

twurl -H upload.twitter.com "/1.1/media/upload.json" -d "command=APPEND&media_id=601491637433475073&segment_index=1" --file ./xab --file-field "media"

twurl -H upload.twitter.com "/1.1/media/upload.json" -d "command=FINALIZE&media_id=601491637433475073" 

{"media_id":601491637433475073,"media_id_string":"601491637433475073","size":6634737,"expires_after_secs":3600,"video":{"video_type":"video\/mp4"}}

"""

    examples["python"] = """

View the code on Github to see how the chunking and media/upload endpoint works:

https://github.com/twitterdev/django-rest-apis/blob/master/home/views.py

"""

    return media(request, "video", examples, 'media_video.html')

@login_required
def media(request, type, examples, template):
    
    api = get_twitter(request.user)
    response = {}
    metadata = None
        
    status = request.REQUEST.get("status", None)
    media_type = request.REQUEST.get("media_type", None)
    upload_url = '%s/media/upload.json' % api.upload_url

    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        
        # save to file
        image = Image(file = file)
        image.save()
        
        media_id = None
        
        if type == "video":
            result = media_upload_chunked(api, upload_url, image, media_type)
            response["media"] = result.get("upload", None)
            media_id = result.get("media_id", None)
            
        else:
            result = media_upload(api, upload_url, image, media_type)
            response["media"] = result.get("upload", None)
            media_id = result.get("media_id", None)
        
        # this is wrong, based on photo vs. video
        if media_id:
            
            data = {'status': status, 'media_ids': [media_id]}
    
            url = '%s/statuses/update.json' % api.base_url
    
            json_data = api._RequestUrl(url, 'POST', data=data)
            data = api._ParseAndCheckTwitter(json_data.content)
            response['tweet'] = data
            
        metadata = get_metadata(image.file.path) 
        print metadata

    context = {'request': request, 'examples': examples, 'form': form, 'response': response, 'metadata': metadata}
    return render_to_response(template, context, context_instance=RequestContext(request))

def media_upload(api, upload_url, image, media_type=None):

    media_id = None
    data = {}
         
    contents = open(str(image.file.path), 'rb').read()

    # using 'media' parameter (binary)
    if media_type == "binary":  
        data['media'] = contents
        
    # using 'media_data' parameter (base64)
    else:                       
        import base64
        contents = base64.b64encode(contents)
        data['media_data'] = contents
        
    json_data = api._RequestUrl(upload_url, 'POST', data=data)
    json_data = json_data.content

    if not 'error' in json_data and not 'errors' in json_data:
        
        response = api._ParseAndCheckTwitter(json_data)
        media_id = response['media_id_string']

    result = {
        "media_id": media_id,
        "upload": json_data
    }
    
    return result

# chunked media upload always does base64 encoded uploads    
def media_upload_chunked(api, upload_url, image, media_type=None):

    import base64

    contents = open(str(image.file.path), 'rb').read()
    contents = base64.b64encode(contents)

    chunks = chunkify(contents, SIZE_5MB) 
        
    # INIT
    data = {
        "command": "INIT", 
        "media_type": "video/mp4", 
        "total_bytes": image.file.size
    }
    
    json_data = api._RequestUrl(upload_url, 'POST', data=data)
    json_data = json.loads(json_data.content)
    media_id = json_data["media_id_string"]

    # APPEND
    count = 0 
    for c in chunks:
        
        data = {
            "command": "APPEND",
            "media_id": media_id,
            "segment_index": count,
            "media_data": c
        }
             
        try:
            json_data = api._RequestUrl(upload_url, 'POST', data=data)
            count = count + 1
            
        except TwitterError as e:
                    
            media_id = None
            json_data = e.args
            break

    if media_id:
    
        # FINALIZE
        data = {
            "command": "FINALIZE", 
            "media_id" : media_id
        }
        
        json_data = api._RequestUrl(upload_url, 'POST', data=data)
        if json_data.status_code == 400:
            media_id = None

        json_data = json.loads(json_data.content)    
        
    result = {
        "media_id": media_id,
        "upload": json_data
    }
    return result

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

def get_metadata(filename):
    
    from hachoir_core.error import HachoirError
    from hachoir_core.cmd_line import unicodeFilename
    from hachoir_parser import createParser
    from hachoir_core.tools import makePrintable
    from hachoir_metadata import extractMetadata
    from hachoir_core.i18n import getTerminalCharset

#     filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, filename)
    if not parser:
        return "Unable to parse file"
    
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        return "Metadata extraction error: %s" % unicode(err)
    
    if not metadata:
        return "Unable to extract metadata"
    
    text = metadata.exportPlaintext()
    return text

def chunkify(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]