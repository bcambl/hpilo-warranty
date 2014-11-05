hpilo-warranty
==============

###Description
Check warranty status on multiple servers via iLO IP.

###Instructions

To install this project:

```
$ git clone https://github.com/bcambl/hpilo-warranty.git
```

```
$ cd hpilo-warranty
```

```
$ git submodules init
```

```
$ git submodules update --remote
```
(*note: `--remote` is important.*)

Create file 'serverlist' in the same directory as checkwarranty.py

```
$ cp examples/serverlist.example serverlist
```

Edit serverlist with a list of iLO IP's or iLO hostnames (one per line)


Run the checkwarranty script

```
$ python checkwarranty.py
```

Once the script has completed, view 'warranty_results.csv' for warranty results


####Credit/Thanks:
http://ocdnix.wordpress.com/

https://github.com/iutrs/hpisee.git
