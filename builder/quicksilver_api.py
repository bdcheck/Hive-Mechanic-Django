def quicksilver_tasks():
    return [
        ('nudge_active_sessions', '--no-color', 10,),
        ('update_cached_graphs', '--no-color', 60,),
        ('update_activity_metadata', '--no-color', 300,),
        ('data_processor_populate_log_items', '--no-color', 60,),
        ('close_expired_sessions', '--no-color', 900,),
    ]
