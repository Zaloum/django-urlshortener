from django.db import models

from random import randrange

MAX_INT = 2147483647

# Create your models here.
class URLRedirect(models.Model):
    original_url = models.URLField(db_index = True)
    times_used   = models.IntegerField(default = 0)
    created      = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.original_url

    @classmethod
    def get_or_create(cls, url):
        """
        Gets the URLRedirect for the url, creating a new one if it does not exist 
        in the database.

        Args:
            original_url: the validated, normalized, and canonicalized url

        Returns:
            the URLRedirect object for the url
        """
        qs = cls.objects.filter(original_url = url)
        if qs.exists():
            # TODO if adding custom urls they should be excluded here
            return qs.first()
        else:
            id = randrange(MAX_INT)
            while cls.objects.filter(id = id).exists(): # birthday paradox. 50% chance of collision after ~55000 entries
                id = randrange(MAX_INT)
            redirect = cls.objects.create(id = id, original_url = url)
            redirect.save()
            return redirect
