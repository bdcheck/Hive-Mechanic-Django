# pylint: disable=no-member,line-too-long

from django.shortcuts import redirect

from .models import TermsVersion, TermsAcceptance

def user_accepted_all_terms(function):
    def wrap(request, *args, **kwargs):
        for terms_vesion in TermsVersion.objects.filter(required=True):
            if TermsAcceptance.objects.filter(user=request.user, terms_version=terms_vesion).count() == 0:
                return redirect('user_required_terms')

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
