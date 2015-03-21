This is a T9 implementation that I wrote a long, long time ago for XBMC
so chat programs could chat via the remote like I could on my Nokia 
phone.

That time has long passed, but the other day I was annoyed with how
ugly it is to enter text on my Samsung Smart TV. They're still using
an alphabetical keyboard, the remote doesn't have letters on it.

The language files are huge, but it's organised so the number of reads 
depends on the number of buttons pressed. It's pretty fast, and uses 
virtually no RAM or CPU. This is required for embedded systems, so
enjoy.

The reader consists of 3 classes, a database node (Py9Key), a database 
client (Py9Dict), and an inputparser (Py9Input). As a user you'll only 
need to bother with the latter.

See demo.py for a good example (works best in a shell), keys are 0-9, 
UDLR (navigation) and S (select mode). You'll need loads of RAM the first 
time you run it, after it's made the DB it'll need hardly any.

  Language files wanted!

  EN-GB: Downloaded from the web, derived from gnu aspell (iirc)
  NL-DU: Thanks to Breght Boschker for submitting these :)

To make your own dictionary, have a read of makePy9.py. 
Keep your wordlists though - the file format might change in future.




