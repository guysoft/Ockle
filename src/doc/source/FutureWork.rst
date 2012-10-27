Future Work
===========
What could be added:

#. Add option to rename server on the webserver
#. Make group webserver functions in to an object-oriented structure.
#. Support to turn on and off a specific server and all its dependents
#. Change Message class to work with json and not xml (so the javascript calls won't hold a mixture of json and xml)
#. Add more generic controllers and testers
#. Add a virtual machine outlets (So an outlet could turn a virtual machine on, not a physical one)
#. More AJAX live updates of the network in the GUI
#. Catastrophe handling - make Ockle start up when major config variables are not set.
#. More Socket communicators apart from the socket handler
#. Make the control/outlet/test scheme more universal
#. Support more types of databases in the logger
#. Get canviz to work with jquery and drop the need for prototype.js
#. Better installer, have a nice bootstrap with main setup options
#. Add more standard methods to pull config variables in the server objects (instead of doing things like ``self.state = json.loads(testerParams["succeed"])`` ).

