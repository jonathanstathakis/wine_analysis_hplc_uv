# Handling Floating Point Errors

So we have a functioning 'SignalMapper' object which combines the actions of peak_map and window_map. we still need to add rounding to all transformers. Doing this will require passing information to the transformers. Preferably, once. It is not a variable to be modified often.

2024-04-17 13:38:31

It is done. A precision mixin class has been defined and added to my custom functions where appropriate. A rounder sklearn transformer has been defined for Pipeline integration.