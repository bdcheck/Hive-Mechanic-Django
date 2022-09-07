# pylint: disable=line-too-long

from six import python_2_unicode_compatible

from django.core.checks import Warning, register # pylint: disable=redefined-builtin

from django.conf import settings
from django.db import models

@register()
def check_data_export_parameters(app_configs, **kwargs): # pylint: disable=unused-argument
    errors = []

    if hasattr(settings, 'DEFAULT_FROM_MAIL_ADDRESS') is False:
        error = Warning('DEFAULT_FROM_MAIL_ADDRESS parameter not defined', hint='Update configuration to include DEFAULT_FROM_MAIL_ADDRESS. (Example: "E-mail Sender <email@example.com>")', obj=None, id='user_creation.W001')
        errors.append(error)

    return errors
    
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='terms_accepted', on_delete=models.CASCADE)
    terms_version = models.ForeignKey(TermsVersion, on_delete=models.CASCADE)
    accepted = models.DateTimeField()

    def __str__(self):
        return '%s - %s (Accepted %s)' % (self.user, self.terms_version, self.accepted)
