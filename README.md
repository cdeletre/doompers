# doompers

Just a simple Python script to automatically check and download new uploaded slides from talks at Troopers. It has been written on the base of Troopers 2017. Not tested for previous years, neither it has been deeply tested for 2017...

Ask help for usage :
```
$ ./main.py -h
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  Write data to FILE
  -v, --verbose         Verbose mode
``

The first run should give you something like this :
```
$ ./main.py
Loading data from troopers-2017.json
Extracting track urls
Adding new tracks
Updating with track data and downloading slides if found
Slide url found for 801, will try to download
Slide url found for 775, will try to download
Slide url found for 774, will try to download
Slide url found for 767, will try to download
Slide url found for 765, will try to download
Slide url found for 755, will try to download
Slide url found for 763, will try to download
Slide url found for 750, will try to download
Slide url found for 756, will try to download
Writing to file troopers-2017.json
Done
$ ls ./slides
750-unsafe-jax-rs-breaking-rest-api.pdf
755-the-metabrik-platform-rapid-development-of-reusable-security-tools.pdf
756-hunting-them-all.pdf
763-intercepting-sap-snc-protected-traffic.pdf
765-protecting-sap-hana-from-vulnerabilities-and-exploits.pdf
767-youve-got-mail-owning-your-business-with-one-email.pdf
774-graph-me-im-famous-automated-static-malware-analysis-and-indicator-extraction-for-binaries.pdf
775-exploring-the-infrared-world-part-2.pdf
801-ripe-atlas-measuring-the-internet.pdf
```
