from django.urls import reverse

def messages_ui_for_player(player):
    player_number = player.player_state.get('messaging_player', None)

    if player_number is not None:
        return '%s?identifier=%s' % (reverse('simple_messaging_ui'), player_number)

    return None
