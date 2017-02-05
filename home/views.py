import base64
import json

from django import forms
from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from social_django.models import UserSocialAuth

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
    examples["twurl"] = "twurl -d 'status=This is a test Tweet' /1.1/statuses/update.json"
    examples["python"] = """
import twitter

api = twitter.Api(
    base_url='https://api.twitter.com/1.1',
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET',
    access_token_key='YOUR_ACCESS_KEY',
    access_token_secret='YOUR_ACCESS_SECRET')
    
api.PostUpdates("This is a test Tweet")
"""
    examples["nodejs"] = """
var Twit = require('twit')

var T = new Twit({
    consumer_key:         'YOUR_CONSUMER_KEY'
  , consumer_secret:      'YOUR_CONSUMER_SECRET'
  , access_token:         'YOUR_ACCESS_KEY'
  , access_token_secret:  'YOUR_ACCESS_SECRET'
})

T.post('statuses/update', { status: 'This is a test Tweet' }, function(err, data, response) {
  console.log(data)
})
"""
    examples["ruby"] = """
client = Twitter::REST::Client.new do |config|
  config.consumer_key        = "YOUR_CONSUMER_KEY"
  config.consumer_secret     = "YOUR_CONSUMER_SECRET"
  config.access_token        = "YOUR_ACCESS_TOKEN"
  config.access_token_secret = "YOUR_ACCESS_SECRET"
end

client.update("This is a test Tweet")
"""
    examples["java"] = """
/*
 * Copyright 2007 Yusuke Yamamoto
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package twitter4j.examples.tweets;

import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.auth.AccessToken;
import twitter4j.auth.RequestToken;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Example application that uses OAuth method to acquire access to your account.<br>
 * This application illustrates how to use OAuth method with Twitter4J.<br>
 *
 * @author Yusuke Yamamoto - yusuke at mac.com
 */
public final class UpdateStatus {
    /**
     * Usage: java twitter4j.examples.tweets.UpdateStatus [text]
     *
     * @param args message
     */
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java twitter4j.examples.tweets.UpdateStatus [text]");
            System.exit(-1);
        }
        try {
            Twitter twitter = new TwitterFactory().getInstance();
            try {
                // get request token.
                // this will throw IllegalStateException if access token is already available
                RequestToken requestToken = twitter.getOAuthRequestToken();
                System.out.println("Got request token.");
                System.out.println("Request token: " + requestToken.getToken());
                System.out.println("Request token secret: " + requestToken.getTokenSecret());
                AccessToken accessToken = null;

                BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
                while (null == accessToken) {
                    System.out.println("Open the following URL and grant access to your account:");
                    System.out.println(requestToken.getAuthorizationURL());
                    System.out.print("Enter the PIN(if available) and hit enter after you granted access.[PIN]:");
                    String pin = br.readLine();
                    try {
                        if (pin.length() > 0) {
                            accessToken = twitter.getOAuthAccessToken(requestToken, pin);
                        } else {
                            accessToken = twitter.getOAuthAccessToken(requestToken);
                        }
                    } catch (TwitterException te) {
                        if (401 == te.getStatusCode()) {
                            System.out.println("Unable to get the access token.");
                        } else {
                            te.printStackTrace();
                        }
                    }
                }
                System.out.println("Got access token.");
                System.out.println("Access token: " + accessToken.getToken());
                System.out.println("Access token secret: " + accessToken.getTokenSecret());
            } catch (IllegalStateException ie) {
                // access token is already available, or consumer key/secret is not set.
                if (!twitter.getAuthorization().isEnabled()) {
                    System.out.println("OAuth consumer key/secret is not set.");
                    System.exit(-1);
                }
            }
            Status status = twitter.updateStatus(args[0]);
            System.out.println("Successfully updated the status to [" + status.getText() + "].");
            System.exit(0);
        } catch (TwitterException te) {
            te.printStackTrace();
            System.out.println("Failed to get timeline: " + te.getMessage());
            System.exit(-1);
        } catch (IOException ioe) {
            ioe.printStackTrace();
            System.out.println("Failed to read the system input.");
            System.exit(-1);
        }
    }
}
"""

    status = request.POST.get("status", None)
    
    api = get_twitter(request.user)
    response = None
    
    if status:
        response = api.PostUpdates(status)[0].AsDict()

    context = {'request': request, 'examples': examples, 'response': response, 'response_pretty': json.dumps(response) }
    return render_to_response('tweet.html', context, context_instance=RequestContext(request))

@login_required
def query(request):
    
    screen_name = request.POST.get("screen_name", None)
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
    examples["nodejs"] = """
var Twit = require('twit')

var T = new Twit({
    consumer_key:         'YOUR_CONSUMER_KEY'
  , consumer_secret:      'YOUR_CONSUMER_SECRET'
  , access_token:         'YOUR_ACCESS_KEY'
  , access_token_secret:  'YOUR_ACCESS_SECRET'
})

T.get('statuses/user_timeline', { screen_name: '%s', count: 200 },  function (err, data, response) {
  console.log(data)
})
""" % (screen_name)
    examples["ruby"] = """
client = Twitter::REST::Client.new do |config|
  config.consumer_key        = "YOUR_CONSUMER_KEY"
  config.consumer_secret     = "YOUR_CONSUMER_SECRET"
  config.access_token        = "YOUR_ACCESS_TOKEN"
  config.access_token_secret = "YOUR_ACCESS_SECRET"
end

client.user_timeline("%s", {count: 200})
""" % (screen_name)
    examples["java"] = """
/*
 * Copyright 2007 Yusuke Yamamoto
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package twitter4j.examples.timeline;

import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;

import java.util.List;

/**
 * @author Yusuke Yamamoto - yusuke at mac.com
 * @since Twitter4J 2.1.7
 */
public class GetUserTimeline {
    /**
     * Usage: java twitter4j.examples.timeline.GetUserTimeline
     *
     * @param args String[]
     */
    public static void main(String[] args) {
        // gets Twitter instance with default credentials
        Twitter twitter = new TwitterFactory().getInstance();
        try {
            List<Status> statuses;
            String user;
            if (args.length == 1) {
                user = args[0];
                statuses = twitter.getUserTimeline(user);
            } else {
                user = twitter.verifyCredentials().getScreenName();
                statuses = twitter.getUserTimeline();
            }
            System.out.println("Showing @" + user + "'s user timeline.");
            for (Status status : statuses) {
                System.out.println("@" + status.getUser().getScreenName() + " - " + status.getText());
            }
        } catch (TwitterException te) {
            te.printStackTrace();
            System.out.println("Failed to get timeline: " + te.getMessage());
            System.exit(-1);
        }
    }
}
"""
    
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
    examples["nodejs"] = """
var Twit = require('twit')
var fs = require('fs')

var T = new Twit({
    consumer_key:         'YOUR_CONSUMER_KEY'
  , consumer_secret:      'YOUR_CONSUMER_SECRET'
  , access_token:         'YOUR_ACCESS_KEY'
  , access_token_secret:  'YOUR_ACCESS_SECRET'
})

var b64content = fs.readFileSync('/path/to/img', { encoding: 'base64' })

// first we must post the media to Twitter
T.post('media/upload', { media_data: b64content }, function (err, data, response) {

  // now we can reference the media and post a tweet (media will attach to the tweet)
  var mediaIdStr = data.media_id_string
  var params = { status: 'Tweet with a photo!', media_ids: [mediaIdStr] }

  T.post('statuses/update', params, function (err, data, response) {
    console.log(data)
  })
})
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
    examples["nodejs"] = ""

    return media(request, "video", examples, 'media_video.html')

@login_required
def media(request, type, examples, template):
    
    log = Log()

    api = get_twitter(request.user)
    response = {}
    metadata = None
        
    status = request.POST.get("status", None)
    media_type = request.POST.get("media_type", None)
    media_category = request.POST.get("media_category", None)
    upload_url = '%s/media/upload.json' % api.upload_url

    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        
        # save to file
        image = Image(file = file)
        image.save()

        # metadata of file        
        metadata = get_metadata(image.file.path) 
        
        media_id = None
        
        if type == "video":
            result = media_upload_chunked(api, upload_url, image, media_type, media_category, log=log)
            response["media"] = result.get("upload", None)
            media_id = result.get("media_id", None)
            
        else:
            result = media_upload(api, upload_url, image, media_type, log=log)
            response["media"] = result.get("upload", None)
            media_id = result.get("media_id", None)
        
        # this is wrong, based on photo vs. video
        if media_id:
            
            data = {'status': status, 'media_ids': [media_id]}
            
            url = '%s/statuses/update.json' % api.base_url

            log.append("%s request: %s" % (url, data))
    
            json_data = api._RequestUrl(url, 'POST', data=data)
            
            json_data = json_data.content
            
            log.append("%s response: %s" % (url, json_data))

            data = None        
            if not 'error' in json_data and not 'errors' in json_data:
                
                data = api._ParseAndCheckTwitter(json_data)

            response['tweet'] = data
            
        response["log"] = log.out()
            
    context = {'request': request, 'examples': examples, 'form': form, 'response': response, 'metadata': metadata}
    return render_to_response(template, context, context_instance=RequestContext(request))

def media_upload(api, upload_url, image, media_type=None, log=None):

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
        
    log.append("%s request: %s" % (upload_url, data))
        
    json_data = api._RequestUrl(upload_url, 'POST', data=data)
    json_data = json_data.content
    
    log.append("%s response: %s" % (upload_url, json_data))

    if not 'error' in json_data and not 'errors' in json_data:
        
        response = api._ParseAndCheckTwitter(json_data)
        media_id = response['media_id_string']

    result = {
        "media_id": media_id,
        "upload": json_data
    }
    
    return result

# chunked media upload always does base64 encoded uploads    
def media_upload_chunked(api, upload_url, image, media_type=None, media_category=None, log=None):

    import base64

    #ffprobe check (TODO: Add this to return or only use in standalone tool?)
    #video_info = ffprobe(image.file.path)
    #print json.dumps(video_info, indent=4)

    contents = open(str(image.file.path), 'rb').read()
    contents = base64.b64encode(contents)

    chunks = chunkify(contents, SIZE_5MB) 
        
    # INIT
    data = {
        "command": "INIT", 
        "media_type": "video/mp4", 
        "total_bytes": image.file.size
    }
    
    if media_category:
        data["media_category"] = media_category
        
    log.append("%s INIT request: %s" % (upload_url, data))
    
    json_data = api._RequestUrl(upload_url, 'POST', data=data)
    json_data = json.loads(json_data.content)
    media_id = json_data.get("media_id_string", None)
    
    log.append("%s INIT response: %s" % (upload_url, json_data))

    if media_id:
        
        # APPEND
        count = 0 
        for c in chunks:
            
            data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": count,
                "media_data": c
            }
            
            log.append("%s APPEND request: segment %s" % (upload_url, count))

            try:
                json_data = api._RequestUrl(upload_url, 'POST', data=data)
                count = count + 1
                
                log.append("%s APPEND response: %s" % (upload_url, json_data))
                
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
        
        log.append("%s FINALIZE request: %s" % (upload_url, media_id))
        
        json_data = api._RequestUrl(upload_url, 'POST', data=data)
        if json_data.status_code == 400:
            media_id = None

        json_data = json.loads(json_data.content)
        
        log.append("%s FINALIZE response: %s" % (upload_url, json_data))
        
        processing_info = json_data.get('processing_info', None)
        
        while processing_info and processing_info.get('state', None) == 'pending':

            check_after_secs = processing_info.get('check_after_secs', None)
                
            import time
            time.sleep(check_after_secs)
                
            # STATUS
            data = {
                "command": "STATUS", 
                "media_id" : media_id
            }

            log.append("%s STATUS request: %s" % (upload_url, data))
            
            json_data = api._RequestUrl(upload_url, 'GET', data=data)
            json_data = json.loads(json_data.content)

            log.append("%s STATUS response: %s" % (upload_url, json_data))

            processing_info = json_data.get('processing_info', None)
                          
    result = {
        "media_id": media_id,
        "upload": json_data,
        "log": log.out()
    }
    return result

@login_required
def media_inspector(request):

    video_info = {}
    video_metadata = None
    ffprobe_exists = True

    if which('ffprobe') == None:
        ffprobe_exists = False
    # TODO: use this flag in view to add instructions to install ffprobe

    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        
        # save to file
        image = Image(file = file)
        image.save()

        # metadata of file        
        #video_metadata = get_metadata(image.file.path) 
        #print video_metadata

        # ffprobe
        if ffprobe_exists:
            video_info = ffprobe(image.file.path)
            print json.dumps(video_info, indent=4)
            
            # Add warning checks
            if video_info.get('streams', None):
                for stream in video_info['streams']:
                    if stream.get('codec_type', None) == "audio":
                        stream['channel_layout_warning'] = (stream.get('channel_layout', None) in ["mono","stereo"])

    context = {'request': request, 'form': form, 'video_info': video_info, 'video_info_pretty': json.dumps(video_info), 'video_metadata': video_metadata, 'ffprobe_exists': ffprobe_exists }
    return render_to_response('media_inspector.html', context, context_instance=RequestContext(request))

# used check if ffprobe exists
def which(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    # short-circuit on heroku 
    FFPROBE_HEROKU = '/app/.heroku/vendor/ffmpeg/bin/ffprobe'
    if is_exe(FFPROBE_HEROKU):
        return FFPROBE_HEROKU

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
            
    return None

def ffprobe(file_path):
    import os
    import subprocess

    if file_path is None:
        return json.loads("{ 'error': 'no file path'}")

    # check if ffprobe exists
    ffprobe_path = which('ffprobe')
    if ffprobe_path == None:
        return json.loads("{ 'error': 'ffprobe not installed'}")

    # check if input file exists
    if not os.path.isfile(file_path):
        return json.loads("{ 'error': 'input file does not exist'}")

    # run ffprobe and get output
    p = subprocess.Popen([ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path ],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        return json.loads("{ 'error': '%s'}" % err)

    # read output and get the packets info
    return json.loads(out)

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

class Log():
    
    y = ""
    
    def append(self, x):
        
        self.y = self.y + "\n" + x
        if settings.DEBUG:
            print x
        
    def out(self):
        
        return self.y
        