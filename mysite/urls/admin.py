from django import forms
from django.contrib import admin

from .models import URLRedirect
from .contrib.base_n import encode

# Register your models here.
class URLRedirectAdmin(admin.ModelAdmin):
    readonly_fields = [ 'id', 'created', 'encoded' ]
    fields          = [
            'id', 
            'encoded', 
            'created', 
            'times_used', 
            'original_url', 
    ]

    def encoded(self, instance):
        return encode(instance.id)

admin.site.register(URLRedirect, URLRedirectAdmin)
