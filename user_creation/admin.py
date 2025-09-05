from django.contrib.gis import admin

from .models import TermsVersion, TermsAcceptance

@admin.register(TermsVersion)
class TermsVersionAdmin(admin.GISModelAdmin):
    list_display = ('name', 'added', 'required',)
    list_filter = ('required', 'added',)

@admin.register(TermsAcceptance)
class TermsAcceptanceAdmin(admin.GISModelAdmin):
    list_display = ('user', 'terms_version', 'accepted',)
    list_filter = ('accepted', 'terms_version',)
