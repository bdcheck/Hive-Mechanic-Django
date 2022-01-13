# pylint: disable=no-member,line-too-long

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import TermsVersion, TermsAcceptance

@login_required
def user_required_terms(request): # pylint: disable=unused-argument
    context = {}

    if request.method == 'POST':
        terms_id = request.POST.get('terms_id', None)

        if terms_id is not None:
            terms_version = TermsVersion.objects.get(pk=int(terms_id))

            TermsAcceptance.objects.create(user=request.user, terms_version=terms_version, accepted=timezone.now())

    for terms_version in TermsVersion.objects.filter(required=True):
        if TermsAcceptance.objects.filter(user=request.user, terms_version=terms_version).count() == 0:
            context['terms'] = terms_version

            return render(request, 'required_terms.html', context=context)

    return redirect('builder_home')
