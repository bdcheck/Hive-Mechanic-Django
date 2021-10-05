# Hive Mechanic Python Client Library

This Python client library is intended to provide secure control of a Hive Mechanic installation from third-party devices and applications.


## Create an API client on the remote Hive Mechanic installation

To begin, log onto your Hive Mechanic installation and create an API client:

    https://my-site.example.com/admin/http_support/apiclient/

Tap the `Add API Client` button in the upper-right of the Django administration interface.

Give the API client a `Name` and `Shared secret`. The shared secret is effectively a password that your client application will use to authenticate itself and interact with the remote Hive Mechanic installation. For best security, generate a longer random secret string instead of using something easily guessable.

If you have not already created an HTTP integration to map this client to a specific game, do so by tapping the `+` button next to the `Integration` select field. Give the integration a unique name and unique `URL slug`. Select a type of `HTTP` and select the target game.


## Client library setup

Once an API client has been created on the remote site, install the client library by cloning this repository from GitHub:

    git clone https://github.com/bdcheck/Hive-Mechanic-Client-Python.git hive_client

Install the library's dependencies:

    pip install -r requirements.txt

At this point, you are ready to begin using the library.


## Client library usage

The following lines illustrate how to use the library:

    from hive_client import HiveClient, VariableScope, TriggerInterruptCommand, SetVariableCommand

    client = HiveClient('https://my-site.example.com/http/', token='api-client-shared-secret')
    
The lines above import the relevant modules into the local namespace and create a `HiveClient` object that will mediate access to the remote API.

The first argument is the path of to the HTTP API interface on the local server. The second `token` argument is the shared secret created when creating the API client.

    commands = [
        TriggerInterruptCommand('BUTTON-PRESSED'),
        SetVariableCommand('button_press_ts', timezone.now().isoformat(), VariableScope.game)
    ]

    response = client.issue_commands(commands, player='pi:12345')

The API functions by sending lists of commands to the remote server (details below). The `player` parameter can be used to specify the specific player under which the commands should be run.

    print('Response: %s', response)

You may inspect the `response` argument to inspect the JSON response from the server. This can provide details for debugging as needed.

    audio_url = client.fetch_variable('claimed_audio_file', scope=VariableScope.game)

    print('Play audio URL: %s', audio_url)

In addition to providing commands to send to the server, the `HiveClient` object also provides some convenience methods for tasks such as inspecting activity variables.


## Client library commands

The following commands are availabel for use with the `HiveClient.issue_commands()` and `HiveClient.issue_command()` methods:

`GotoCommand`: Advances a player's dialog to a specified card in the activity. 

Parameters:

* `destination` (required): identifier of the destination card.

---

`TriggerInterruptCommand`: Triggers an interrupt keyword in the activity, directing the player to advance to the specified card in the activity's settings. 

Parameters:

* `keyword` (required): keyword to trigger.

---

`SetVariableCommand`: Sets a variable in the specified scope for the specific game. 

Parameters:

* `name` (required): Name of the variable to set.
* `value` (required): Value to set to the variable.
* `scope` (required): Scope of the variable. May be one of `VariableScope.game`, `VariableScope.player`, or `VariableScope.session`.


## Client library methods

`client = new HiveClient(api_url, token, timeout, logger)`: Creates a new `HiveClient` instance.

Parameters:

* `api_url` (required): URL endpoint of the HTTP API on the remote Hive Mechanic installation.
* `token` (required): Shared secret set up on the remote server.
* `timeout`: Timeout in seconds when to raise an exception to allow the calling application to continue while the server remains unresponsive. (Default: `60`)
* `logger`: Python logger object to use to log any issues or other output from the client library. If none is provided, a new one is created that outputs to the standard output stream.

---

`client.issue_commands(commands, player)`: Transmits a series of commands to the remote Hive Mechanic installation.

Parameters

* `commands` (required): A Python `list` or `tuple` containing the sequence of commands to transmit to the server. Each item in the list is a command object (see above) instantiated with the relevant arguments.
* `player`: Specified player to use when executing the commands on the server. If the player does not exist, the remote server may or may not create a new player and session for the activity. (This parameter is configured when creating the HTTP Integration on the server side.)

---

`client.issue_command(command, player)`: Transmits one command to the remote Hive Mechanic installation. This is a convenience method for `issue_commands`.

Parameters

* `command` (required): A command object (see above) instantiated with the relevant arguments.
* `player`: Specified player to use when executing the commands on the server. If the player does not exist, the remote server may or may not create a new player and session for the activity. (This parameter is configured when creating the HTTP Integration on the server side.)

---

`client.fetch_variable(variable, player, default, scope)`: Synchronously retrieves a variable from the server mapped to the provided parameters.

Parameters

* `variable` (required): Remote variable name
* `player`: Specified player to use retrieving player- or session-scoped variables. (Default: `None`)
* `default`: Fallback value to provide if the variable is not available on the server or has not been set. (Default: `None`)
* `scope`: Specified scope to search for variable. May be one of `VariableScope.game`, `VariableScope.player`, or `VariableScope.session`. (Default: `VariableScope.game`)
