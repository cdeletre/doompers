#!/usr/bin/env python
# coding: utf-8

import requests
import json
from os import path
from os import makedirs
from urlparse import urlparse
from optparse import OptionParser

URLS = {}
URLS [u'ngi'] = u'https://www.troopers.de/troopers18/ngi/'
URLS [u'conf'] = u'https://www.troopers.de/troopers18/agenda/'
URLS [u'tsd'] = u'https://www.troopers.de/troopers18/telco-sec-day/'

JFILENAME = u'troopers-2018.json'

SLIDESPATH = u'./slides/'

DEBUG = False
TEXT_ONLY = False
RE_DOWNLOAD = False

def debug(msg):
    global DEBUG
    if DEBUG:
        print(msg)

def toggle_debug():
    global DEBUG
    DEBUG = not DEBUG

def toggle_textonly():
    global TEXT_ONLY
    TEXT_ONLY = not TEXT_ONLY

def toggle_redownload():
    global RE_DOWNLOAD
    RE_DOWNLOAD = not RE_DOWNLOAD

def write_jfile(filename,data):
    # Write JSON data to file

    fjson = open(filename,b'w+')
    fjson.write(json.dumps(data,indent=4, separators=(',', ': ')))
    fjson.close()

def load_jfile(filename):
    # Load and return JSON data loaded from a file

    data = {}

    if path.exists(filename):

        try:
            fjson = open(filename,b'r')
            data = json.load(fjson)
            debug(u'%s contains data will try to reuse them' % filename)
            fjson.close()
        except Exception as err:
            debug(u'%s does not seem to contain data, will use default URL settings' % filename)
    else:
        debug(u'%s does not seem to exist, will create it and use default URL settings' % filename)

    return data

def get_track_id(url):
    # Return the track ID from the url

    return url.split('/')[::-1][0].split('-')[0]

def get_track_name(url):
    # Return track name from url

    return url.split('/')[::-1][0]

def get_url_root(url):
    # Return root from url

    return '{uri.scheme}://{uri.netloc}'.format(uri=urlparse( url ))

def get_url(data,key):
    # Return url for specific event (conf/tsd/ngi) from JSON data
    # If not found set default value

    if key not in data.keys() or u'url' not in data[key].keys() or data[key]['url'] == u'':
            debug(u'Setting default url for %s' % key)
            data[key] = {}
            data[key]['url'] = URLS[key]
            data[key][u'tracks'] = {}

    return data[key]['url']

def add_tracks(data,key,new_urls,conf_urls):
    # Add to JSON data new track(s) from new_urls for specific event (conf/tsd/ngi)
    # Remove url duplicated in conf_urls

    for url in new_urls:
        id = get_track_id(url)
        if id not in data[key][u'tracks'].keys():
            debug(u'Add new track %s' % id)
            data[key][u'tracks'][id] = {}
            data[key][u'tracks'][id][u'url'] = url

        if url in conf_urls:
            conf_urls.remove(url)


def update_tracks(data,key):
    # Update track in JSON data for specific event (conf/tsd/ngi)

    global TEXT_ONLY
    global RE_DOWNLOAD

    for i,id in enumerate(data[key][u'tracks']):
        track = data[key][u'tracks'][id]
        if u'url_slides' in track.keys() and track[u'url_slides'] == u'' or u'url_slides' not in track.keys():
            # No slides url previously found or data for this track never dumped 
            title,description,url_slides,speaker,about_speaker = extract_track_data(track[u'url'])

            if url_slides != u'' and not TEXT_ONLY:
                # Slides were found
                print(u'Slide url found for %s, will try to download' % id)
                download_slides(url_slides, get_track_name(track[u'url']))

            # Save data for this track
            track[u'title'],track[u'description'],track[u'url_slides'],track[u'speaker'],track[u'about_speaker'] = title,description,url_slides,speaker,about_speaker

        elif RE_DOWNLOAD and u'url_slides' in track.keys() and track[u'url_slides'] != u'':
            # Re-download slides
            print(u'Redownloading slides %s' % id)
            download_slides(track[u'url_slides'], get_track_name(track[u'url']) )

def extract_track_urls(url):
    # Return track urls detected at url

    debug(u'Retriving track urls from %s' % url)
    track_urls = []
    url_root = get_url_root(url)

    r_body = requests.get(url)

    if r_body.status_code != 200:
        debug(u'Can get the page :(')
        debug (r_body.status_code)
    else:
        content = r_body.content.decode('utf-8')
        for line in content.split(u'\n'):
            if u'<a class="event-name"' in line:
                track_url = url_root + line.split(u'"')[3]
                debug(u'Found track url: %s' % track_url)
                track_urls.append(track_url)

    return track_urls
        

def extract_track_data(track_url):
    # Return track data found at track_url

    debug('Retriving track data from %s' % track_url)
    title = u''
    speaker = u''
    about_speaker = u''
    description = u''
    url_slides = u''

    r_track = requests.get(track_url)

    if r_track.status_code != 200:
        debug(u'Can get the track page :(')
        debug(r_track.status_code)
    else:
        step = 0
        content = r_track.content.decode('utf-8')
        for line in content.split(u'\n'):
            line = line.strip()
            if step == 0 and u'<main class="event__info">' in line:
                debug(u'Found event section')
                step = 1
            elif step == 1 and u'<h1>' in line:
                title = line.split(u'>')[1].split(u'<')[0]
                step = 2
            elif step == 2 and u'<aside class="event__info__meta">' in line:
                debug(u'Found meta info section')
                step = 3
            elif step == 3 and u'<div>' in line:
                debug(u'Found description section')
                step = 4
            elif step == 4 and u'<p><a href=' in line:
                debug(u'Found slides url')
                url_slides = line.split(u'"')[1]
            elif step == 4 and u'<p>' in line:
                description += line + u'\n'
            elif step == 4 and u'</div>' in line:
                step = 5
            elif step == 5 and u'<div class="event__speakers">' in line:
                step = 6
            elif step == 6 and u'<span class="icon-label">' in line:
                speaker = line.split(u'>')[1].split(u'<')[0]
                debug(u'Found speaker')
                step = 7
            elif step == 7 and u'<article class="bio">' in line:
                debug(u'Found speaker bio')
                step = 8
            elif step == 8 and u'<p>' in line:
                about_speaker = line + u'\n'
            elif step == 8 and u'</article>' in line:
                break
    return title,description,url_slides,speaker,about_speaker

def download_slides(url,name):
    # Download slides at url with name as filename (witout extension)

    r_slides = requests.get(url)

    if r_slides.status_code != 200:
        debug(u'Cannot download slides :(')
        debug(r_slides.status_code)
    else:
        debug(u'Downloading %s' % url)
        if not path.exists(SLIDESPATH):
            makedirs(SLIDESPATH) 
        filename = name + '.' + url.split('.')[::-1][0]
        fslides = open('./slides/' + filename, b'w+')
        fslides.write(r_slides.content)
        fslides.close()
        debug(u'%s written' % filename)

def main():

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", default=JFILENAME, help="Write track data to FILE (%s by default)" % JFILENAME, metavar="FILE")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose mode")
    parser.add_option("-t", "--text-only", action="store_true", dest="textonly", default=False, help="Text only, no slides are downloaded")
    parser.add_option("-r", "--re-download", action="store_true", dest="redownload", default=False, help="Re-download slides")
    (options, args) = parser.parse_args()

    if options.verbose:
        toggle_debug()

    if options.textonly and options.redownload:
        print(u'You have to make a choice between text only and re-downloading')
        return

    if options.textonly:
        toggle_textonly()

    if options.redownload:
        toggle_redownload()

    print(u'Loading data from %s' % options.filename)
    jdata = load_jfile(options.filename)

    url_conf = get_url(jdata,u'conf')
    url_tsd = get_url(jdata,u'tsd')
    url_ngi = get_url(jdata,u'ngi')

    # Detect track urls
    print(u'Extracting track urls')
    conf_track_urls = extract_track_urls(url_conf)
    ngi_track_urls = extract_track_urls(url_ngi)
    tsd_track_urls = extract_track_urls(url_tsd)

    # Add new tracks
    print(u'Adding new tracks')
    add_tracks(jdata,u'ngi',ngi_track_urls,conf_track_urls)
    add_tracks(jdata,u'tsd',tsd_track_urls,conf_track_urls)
    add_tracks(jdata,u'conf',conf_track_urls,[])

    # Update data 
    print(u'Updating with track data and downloading slides if found')
    update_tracks(jdata,u'tsd')
    update_tracks(jdata,u'ngi')
    update_tracks(jdata,u'conf')

    # save work done in file
    print(u'Writing to file %s' % options.filename)
    write_jfile(options.filename,jdata)
    
    print(u'Done')

main()
