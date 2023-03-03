# pylint: disable=line-too-long, no-member

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

    tags = models.ManyToManyField(LogTag, blank=True)

    player = models.ForeignKey('builder.Player', null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey('builder.Session', null=True, blank=True, on_delete=models.SET_NULL)
    game_version = models.ForeignKey('builder.GameVersion', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s[%s]: %s (%s)' % (self.source, self.logged, self.message, self.tags_str())

    def tags_str(self):
        return 'TODO'

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
