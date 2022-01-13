from six import python_2_unicode_compatible

from django.conf import settings
from django.db import models

@python_2_unicode_compatible
class TermsVersion(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    added = models.DateTimeField()
    required = models.BooleanField(default=True)
    terms_html = models.FileField(upload_to='terms_html')

    def __str__(self):
        return '%s' % self.name

@python_2_unicode_compatible
class TermsAcceptance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    terms_version = models.ForeignKey(TermsVersion, on_delete=models.CASCADE)
    accepted = models.DateTimeField()

    def __str__(self):
        return '%s - %s (Accepted %s)' % (self.user, self.terms_version, self.accepted)
