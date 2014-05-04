from django.shortcuts import *

# Create your views here.
def home(request):
    context = {}
    return render_to_response('home.html', context, context_instance=RequestContext(request))
