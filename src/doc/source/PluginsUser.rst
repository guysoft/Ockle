Plugins List
============

One of Ockle's main features is that its completely plugin-driven. So functionality can be switch on or off by enabling and disabling plugins.

Disabling plugins can be done in ``etc/config.ini`` in the ``[plugins]`` section under ``plugins``, or via the GUI in the general section of the configuration tab.

Plugins
-------

- **AutoControl** - When enabled gives automatic commands requiring switching the whole network.
- **CoreCommunicationCommands** - This plugin gives basic communication commands such as listing the existing servers, their states etc.
- **EditingCommunicationCommands** - When enabled modifying INI files is possible via remote clients.
- **Logger** - This plugin logs periodically data from the outlets and controllers in all servers.
- **SocketListener** - This plugin enables sending commands to Ockle via server sockets.