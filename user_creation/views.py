# pylint: disable=no-member,line-too-long

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import password_validators_help_texts, validate_password
from django.core.mail import send_mail
from django.core.validators import validate_email, ValidationError
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
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

@login_required
def user_terms_view(request): # pylint: disable=unused-argument
    context = {}

    context['latest_terms'] = request.user.terms_accepted.order_by('-accepted').first()

    if context['latest_terms'] is not None:
        context['terms'] = context['latest_terms'].terms_version

        return render(request, 'required_terms_view.html', context=context)

    return redirect('builder_home')

def user_request_access(request): # pylint: disable=unused-argument, too-many-branches
    context = {
        'password_requirements': password_validators_help_texts(),
        'errors': []
    }

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        email = request.POST.get('email', None)

        if name == '':
            context['errors'].append('Please provide a name.')

        try:
            validate_email(email)
        except ValidationError:
            context['errors'].append('Invalid e-mail address.')

        password = request.POST.get('password', None)
        confirm_password = request.POST.get('confirm_password', None)

        if password is None or password != confirm_password:
            context['errors'].append('Empty or non-matching passwords.')
        else:
            try:
                validate_password(password)
            except ValidationError as validation_error:
                for message in validation_error.messages:
                    context['errors'].append(message)

        if len(context['errors']) == 0: # pylint: disable=len-as-condition
            if get_user_model().objects.filter(username=email).count() == 0:
                new_user = get_user_model().objects.create_user(username=email, email=email, password=password, is_active=False)

                names = name.split()

                new_user.last_name = names[-1]

                if len(names) > 1:
                    new_user.first_name = ' '.join(names[:-1])

                new_user.save()

                to_addrs = []

                admins_group = Group.objects.filter(name='Hive Mechanic Manager').first()

                if admins_group is not None:
                    for user in admins_group.user_set.all():
                        if user.has_perm('auth.change_user') and user.email is not None:
                            to_addrs.append(user.email)
                else:
                    for user in get_user_model().objects.all():
                        if user.has_perm('auth.change_user') and user.email is not None:
                            to_addrs.append(user.email)

                if to_addrs:
                    subject = 'New Hive Mechanic Access Request (' + settings.ALLOWED_HOSTS[0] + ')'

                    message = render_to_string('new_user_message.txt', {
                        'user': new_user,
                        'settings': settings,
                        'update_url': reverse('builder_authors')
                    })

                    send_mail(subject, message, settings.DEFAULT_FROM_MAIL_ADDRESS, to_addrs, fail_silently=False)

            return render(request, 'user_request_access_complete.html', context=context)

    return render(request, 'user_request_access.html', context=context)

@login_required
def user_account(request): # pylint: disable=unused-argument
    context = {}

    context['password_requirements'] = password_validators_help_texts()

    context['messages'] = []

    if request.method == 'POST':
        email = request.POST.get('email', '')

        if email != request.user.email:
            request.user.email = email
            request.user.username = email

            request.user.save()

            context['messages'].append('E-mail address updated successfully.')

        current_password = request.POST.get('current-password', None)
        new_password = request.POST.get('new-password', None)

        if new_password is not None and new_password != '': # nosec
            if request.user.check_password(current_password) is True:
                try:
                    validate_password(new_password, user=request.user)
                    request.user.set_password(new_password)
                    request.user.save()
                    context['messages'].append('Password updated successfully.')
                except ValidationError as error:
                    for validation_error in error.messages:
                        context['messages'].append('Unable to update password: ' + str(validation_error))
            else:
                context['messages'].append('Unable to update password, invalid current password provided.')

    context['user'] = request.user
    context['latest_terms'] = request.user.terms_accepted.order_by('-accepted').first()

    return render(request, 'user_account.html', context=context)
