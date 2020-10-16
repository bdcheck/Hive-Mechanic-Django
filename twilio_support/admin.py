# pylint: disable=line-too-long
# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import OutgoingMessage, IncomingMessage, OutgoingCall, IncomingCallResponse, IncomingMessageMedia

def send_message(modeladmin, request, queryset): # pylint: disable=unused-argument
    for message in queryset:
        if message.sent_date is None:
            message.transmit()

send_message.description = 'Send pending message'

@admin.register(OutgoingMessage)
class OutgoingMessageAdmin(admin.ModelAdmin):
    list_display = ('destination', 'send_date', 'sent_date', 'message', 'errored')
    search_fields = ('destination', 'message', 'transmission_metadata',)
    list_filter = ('errored', 'send_date', 'sent_date',)

    actions = [send_message]

@admin.register(IncomingMessage)
class IncomingMessageAdmin(admin.ModelAdmin):
    list_display = ('source', 'receive_date', 'message')
    search_fields = ('message', 'source',)
    list_filter = ('receive_date',)

@admin.register(IncomingMessageMedia)
class Admin(admin.ModelAdmin):
    list_display = ('message', 'index', 'content_url', 'content_type')
    search_fields = ('content_url', 'content_type',)
    list_filter = ('content_type',)

def initiate_call(modeladmin, request, queryset): # pylint: disable=unused-argument
    for call in queryset:
        if call.sent_date is None:
            call.transmit()

initiate_call.description = 'Initiate outgoing calls'

def reset_call(modeladmin, request, queryset): # pylint: disable=unused-argument
    for call in queryset:
        call.sent_date = None
        call.errored = False
        call.transmission_metadata = {}
        call.save()

reset_call.description = 'Reset outgoing calls'

@admin.register(OutgoingCall)
class OutgoingCallAdmin(admin.ModelAdmin):
    list_display = ('destination', 'send_date', 'sent_date', 'start_call', 'message', 'file', 'next_action', 'errored')
    search_fields = ('destination', 'message', 'transmission_metadata', 'next_action',)
    list_filter = ('errored', 'send_date', 'sent_date', 'next_action',)
    actions = [initiate_call, reset_call]

    fieldsets = [
        ('Required Properties', {
            'fields': [
                'destination',
                'send_date',
                'sent_date',
                'start_call',
                'message',
                'file',
                'transmission_metadata',
                'integration',
                'next_action',
            ]
        }),
        ('Pause Options', {
            'fields': [
                'pause_length',
            ],
            'classes': ['collapse']
        }),
        ('Gather Options', {
            'fields': [
                'gather_input',
                'gather_finish_on_key',
                'gather_num_digits',
                'gather_timeout',
                'gather_speech_timeout',
                'gather_speech_profanity_filter',
                'gather_speech_model',
            ],
            'classes': ['collapse']
        }),
    ]

@admin.register(IncomingCallResponse)
class IncomingCallResponseAdmin(admin.ModelAdmin):
    list_display = ('source', 'receive_date', 'message')
    search_fields = ('message', 'source',)
    list_filter = ('receive_date',)
