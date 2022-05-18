import praw
import requests
import shutil
import os, io
import codecs
import re
import random
import urllib.request, urllib.error
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen
import glob
import time
# import gallery_get

# my imports
import classes
import pickler






# START PROGRAM
def main():
    # login into
    reddit_home_url = 'https://www.reddit.com'

    settings_file = 'data/settings.dat'
    settings = pickler.load(settings_file)

    scrapper_config = pickler.load(settings['scrapper_config_file'])

    media_dir = settings['media_dir']

    posts_data_file = settings['posts_data_file']
    tags_file = settings['tags_file']
    groups_file = settings['groups_file']

    

    # read the tag, group and old saved post data if they exist
    tags = pickler.load(tags_file)
    groups = pickler.load(groups_file)
    old_posts = pickler.load(posts_data_file)


    # login to reddit and setup a connection
    reddit = praw.Reddit(client_id=scrapper_config['client_id'],
                            client_secret=scrapper_config['client_secret'],
                            user_agent='Post browser for /u/' + scrapper_config['username'],
                            username=scrapper_config['username'],
                            password=scrapper_config['password'])

    print("Connected to reddit instance")

       