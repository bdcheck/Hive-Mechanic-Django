from django.apps import AppConfig


class ActivityLoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'System Activity Logs'
    name = 'activity_logger'
