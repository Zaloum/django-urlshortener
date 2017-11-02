from django.views import generic
from django.http import JsonResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse
from django.db.models import F

from .models import URLRedirect
from .contrib.base_n import encode, decode
from .contrib.urls import hostname, canonicalize, validate_url, ValidationError

# Create your views here.
MAX_DECODE_LENGTH = 10 # 10 ** len(base_n.alphabet) > model.IntegerField.max

class IndexView(generic.TemplateView):
    template_name = 'urls/index.html'

class CreateURLView(generic.View):
    """
    A View to create the shortened urls. Used by AJAX and not designed to be accessed from 
    the address bar.
    """

    def post(self, request):
        url = request.POST.get('url')
        if not url:
            return JsonResponse({
                'success': False, 
            })
        url = canonicalize(url.strip())
        host = hostname(url)
        if host == '':
            host = url
        try:
            validate_url(url)
            redirect = URLRedirect.get_or_create(url) 
        except ValidationError as e:
            return JsonResponse({ 
                'success': False, 
                'url': url, 
                'hostname': host, 
                'result':  e.message
            })

        return JsonResponse({
            'success': True, 
            'url': url, 
            'result': request.build_absolute_uri(
                reverse('urls:redirect', args = ( 
                    encode(redirect.id), 
                ))), 
            'hostname': host, 
            'times_used': redirect.times_used, 
        })


class RedirectURLView(generic.View):
    """
    A View which decodes the kwarg in the url and redirects to either the mapped original url, 
    or if it has not been created, the urls index.
    """

    def get(self, request, *args, **kwargs):
        short = kwargs.get('short')
        if len(short) > MAX_DECODE_LENGTH:
            # not in the database as the decoded 
            # value will definitely be too large.
            return HttpResponseRedirect(reverse('urls:index'))

        try:
            pk = decode(short) 
            redirect = URLRedirect.objects.get(pk = pk)
            redirect.times_used = F('times_used') + 1
            redirect.save(update_fields = [ 'times_used'] )
            return HttpResponsePermanentRedirect(redirect.original_url)
        except (KeyError, URLRedirect.DoesNotExist):
            # KeyError                  invalid characters in url 
            # URLRedirect.DoesNotExist  url has not been created
            return HttpResponseRedirect(reverse('urls:index'))
            
