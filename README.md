# HAPI-Server-Tester
a script written in python to check random datasets on HAPI servers 
Intended for HAPI Consortium use.  It currently uses a hard-coded servers list.

Future improvements:
* Get servers list from https://hapi-server.org/servers/
* Better logging
* a method to capture the seed that random.choice() uses to select random datasets/parameters, so that my test process can be reproduced artificially
* A “data size cap” to prevent my script from trying to download files that are too large(a very rare edge case)
