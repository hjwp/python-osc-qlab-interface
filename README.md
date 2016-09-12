Mostly a bunch of scripts I knocked together to do date import + export and cue renumbering for a show I was involved in.

The main file I expect would conceivably be useful to someone else would be [qlab_interface.py](qlab_interface.py),
which combines a UDP OSC client (based on python-osc) with a server thread that can read the responses that come back asynchronously from qlab.
