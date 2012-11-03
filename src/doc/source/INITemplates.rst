INI Template file format
========================

.. note:: INI Template file format is only accessible by developers, it should not be changed by users.

Ockle has various configuration directives that are set in a common INI Template file format.
By using these templates Ockle module developers simply specify what configuration variables their module has, and Ockle's core would let the user edit them comfortably in the gui. 

These files define how the INI configuration files should be written.

Available settings data types
-----------------------------

INI Template files include the variable name as items, and a json formatted list with the type followed by a default variables. 

Current types supported:

+---------------------+-------------------------------------------+--------------------------------+
|Type                 |Field                                      |Example                         |
+=====================+===========================================+================================+
| string              | default                                   | ["string","yay"]               |
+---------------------+-------------------------------------------+--------------------------------+
| int                 | default                                   | ["int",1]                      |
+---------------------+-------------------------------------------+--------------------------------+
| bool                | default                                   | ["bool",true]                  |
+---------------------+-------------------------------------------+--------------------------------+
| intrange            | default, range                            | ["intrange",1,"1-8"]           |
+---------------------+-------------------------------------------+--------------------------------+
| select :sup:`*`     | select disabled?                          | ["select",false]               |
+---------------------+-------------------------------------------+--------------------------------+
| multilist :sup:`*`  | ordered? , sorted?, Url Pattern :sup:`**` | ["multilist",true,"~~name~~"]  |
+---------------------+-------------------------------------------+--------------------------------+

| :sup:`*` These require the mulichoice variable to be defined
| :sup:`**` ~~name~~ string would be replaced by the multichoice's value
