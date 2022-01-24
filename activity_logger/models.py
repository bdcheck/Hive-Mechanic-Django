import json

from six import python_2_unicode_compatible

from django.conf import settings
from django.db import models
from django.utils import timezone

from builder.models import Player, Session, GameVersion

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

    def tags_str(self):
        return 'TODO'

    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(Session, null=True, blank=True, on_delete=models.SET_NULL)
    game_version = models.ForeignKey(GameVersion, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s[%s]: %s (%s)' % (self.logged, self.source, self.message)

def log(source, message, tags=list, metadata=None, player=None, session=None, game_version=None):
    if metadata is None:
        metadata = {}

    log_item = LogItem.objects.create(source=source, message=message, logged=timezone.now(), metadata=json.dumps(metadata, indent=2))
    
    for tag in tags:
        tag_obj = LogTag.objects.filter(tag=tag).first()
        
        if tag_obj is None:
            tag_obj = LogTag.objects.create(tag=tag, name=tag)
            
        log_item.tags.add(tag_obj)
