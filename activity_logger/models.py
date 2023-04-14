# pylint: disable=line-too-long,no-member

import json

from six import python_2_unicode_compatible

from django.db import models
from django.utils import timezone

@python_2_unicode_compatible
class LogTag(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    tag = models.CharField(max_length=4096, unique=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.tag)

@python_2_unicode_compatible
class LogItem(models.Model):
    source = models.CharField(max_length=4096)
    message = models.TextField(max_length=(4096 * 1024))
    logged = models.DateTimeField()
    metadata = models.TextField(max_length=(4096 * 1024))

    tags = models.ManyToManyField(LogTag, blank=True, related_name='log_items')

    player = models.ForeignKey('builder.Player', null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey('builder.Session', null=True, blank=True, on_delete=models.SET_NULL)
    game_version = models.ForeignKey('builder.GameVersion', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s[%s]: %s (%s)' % (self.source, self.logged, self.message, self.tags_str())

    def tags_str(self): # pylint: disable=no-self-use
        return '(Coming soon)'

    def player_str(self):
        metadata = self.fetch_metadata()

        if metadata is not None and isinstance(metadata, dict):
            player = metadata.get('player', None)

            if player is not None:
                return 'twilio_player:XXXXXX%s' % player[-4:]

        return ''

    def details_json(self):
        details = {}

        metadata = self.fetch_metadata()

        if metadata is not None and isinstance(metadata, dict):
            details['hive_player'] = metadata.get('player', '')
            details['hive_session'] = '(Coming soon)'
            details['game_version'] = metadata.get('game', '')

        return json.dumps(details)

    def fetch_metadata(self):
        if self.metadata is None or self.metadata == '':
            return {}

        return json.loads(self.metadata)

    def update_metadata(self, new_metadata):
        metadata = self.fetch_metadata()

        metadata.update(new_metadata)

        self.metadata = json.dumps(metadata, indent=2)
        self.save()

    def preview_count(self):
        metadata = self.fetch_metadata()

        if metadata is not None and isinstance(metadata, dict):
            return len(metadata.get('media_files', []))

        return 0

    def has_preview(self):
        return self.preview_count() > 0

    def preview(self):
        metadata = self.fetch_metadata()

        media_files = metadata.get('media_files', [])

        if len(media_files) > 0:
            return media_files[0]

        return None

def log(source, message, tags=list, metadata=None, player=None, session=None, game_version=None): # pylint: disable=too-many-arguments
    if metadata is None:
        metadata = {}

    log_item = LogItem.objects.create(source=source, message=message, logged=timezone.now(), metadata=json.dumps(metadata, indent=2))

    for tag in tags:
        tag_obj = LogTag.objects.filter(tag=tag).first()

        if tag_obj is None:
            tag_obj = LogTag.objects.create(tag=tag, name=tag)

        log_item.tags.add(tag_obj)

    if player is not None:
        log_item.player = player

    if session is not None:
        log_item.session = session

    if game_version is not None:
        log_item.game_version = game_version

    log_item.save()
