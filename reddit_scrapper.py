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

from database import Session
from models import Post



def get_valid_filename(string):
    string = str(string).strip().replace(' ', '_')
    string = (string[:75] + '..') if len(string) > 75 else string
    return re.sub(r'(?u)[^-\w.]', '', string)

def add_subbreddit_as_tag(posts, tags):
    for post in posts:
        post.add_tag(post.subreddit)
        if not post.subreddit in tags:
            tags.append(post.subreddit)
    return posts, tags

def scrape_posts(reddit, saved_files, scrape_amount, media_dir):
    num_posts = get_posts_from(reddit.user.me().saved(limit=scrape_amount), saved_files, scrape_amount, media_dir)

    # it is not adding the two lists together like each line an element, kinda doing it 3d
    # posts.append(get_posts_from(reddit.user.me().upvoted(limit=scrape_amount)))
    # print(len(posts), s_posts)
    return num_posts

def get_posts_from(model, saved_files, scrape_amount, media_dir):

    session = Session()
    
    i = 0
    num_new_posts = 0
    for p in model:
        if isinstance(p, praw.models.Submission) and p.over_18: # if the post is a Submission and 18+
            # SQL
            # need to get filename and extension before this


            saved_file, filename, ext = get_media(p.url, p.title, saved_files, media_dir)
            if saved_file:
                # check if the filename is legit, long enough since that is a possible error
                post = Post(p.title, str(p.author), str(p.subreddit), p.url, p.permalink, filename, media_dir, ext)
                session.add(post)
                session.commit()
                num_new_posts += 1
                
        i += 1
        if i % 50 == 0:
            print("scraped {}/{}".format(i, scrape_amount))
    print("scraped a total of {} posts".format(i))
    return num_new_posts

def download_redgif_content(url, filename):
    """Steps in-order.
    * request html
    * get content
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    request_url = Request(url, headers=headers)
    CONTENT_RE = re.compile(r'https:\/\/[a-z0-9]+.redgifs.com\/\w+.mp4')

    # check if the url is a 404 page and ignore those
    try:
        conn = urlopen(request_url)
    except urllib.error.HTTPError as e:
        time.sleep(1)
        print("HTTPError: {} - {}".format(e.code, url))
    except urllib.error.URLError as e:
        print("URLError: {} - {}".format(e.code, url))
    else:
        print("Downloading: {}".format(url))
        with urlopen(request_url) as response:
            html = response.read().decode('utf-8')

        if re.search(CONTENT_RE, html):
            content = re.search(CONTENT_RE, html).group(0)
            
            # redgif files are mp4
            req = Request(content, headers=headers)
            with urlopen(req) as downloaded:
                with open(filename, 'wb') as f:
                    f.write(downloaded.read())
    return True

def download_media(url, filename):
    print("Downloading: {}".format(url))
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return True

# gets the media from the site
# depends on the site
# may break if the site changes how it works
def get_media(url, title, saved_files, media_dir):
    # different urls require us to change either the extension or how we download
    # we would like to check before downloading a file that it doesnt already exists in our database
    # a post already exists in our database if the title, author, and subreddit all match
    # lets assume if we call this function we want to download the file
    # so that means download as long as its possible
    # we return if it was downloaded or not only

    downloaded = False
    
    filename = get_valid_filename(title)
    ext = ''
    # use a function someone made to get the media from redgifs
    if "redgifs" in url:
        ext = 'mp4'

        full_filename = f'{media_dir}/{filename}.{ext}'
        
        downloaded = download_redgif_content(url, full_filename)
    
    # simply download the picture,  this link is to a .jpg
    elif "i.redd.it" in url or ("imgur.com" in url and not "imgur.com/a/" in url) or "cdni.pornpics.com" in url:
        if ".gifv" in url:
            ext = 'mp4'
            url = url[0:-4]+"mp4"
        elif ".gif" in url:
            ext = 'gif'
        elif ".jpg" in url:
            ext = 'jpg'
        elif ".jpeg" in url:
            ext = 'jpeg'
        
        full_filename = f'{media_dir}/{filename}.{ext}'
        downloaded = download_media(url, full_filename)
        


    # for now ignore galleries
    elif "reddit.com/gallery" in url:
        # can use gallery_get to get the pictures
        # but since there is multiple pictures we need to make multiple posts then,
        # same title but with a number to indicate which image of the post we have
        print("Is gallery")
        

    # can change the extension of .gifv to .mp4 and they work????
    elif ".gifv" in url:
        ext = 'mp4'
        url = url[0:-4]+"mp4"
        
        full_filename = f'{media_dir}/{filename}.{ext}'
        download_media(url, full_filename)


    if not downloaded:
        print("Could not find a way to download {}".format(url))


    return downloaded, filename, ext

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

    # amount of posts to scrape, max is 1000
    scrape_amount = scrapper_config['scrape_amount']


    # read the tag, group and old saved post data if they exist
    tags = pickler.load(tags_file)
    groups = pickler.load(groups_file)
    old_posts = pickler.load(posts_data_file)


    # login to reddit and setup a connection
    reddit = praw.Reddit(client_id=scrapper_config['client_id'],
                            client_secret=scrapper_config['client_secret'],
                            user_agent='Post scraper for /u/' + scrapper_config['username'],
                            username=scrapper_config['username'],
                            password=scrapper_config['password'])

    print("Connected to reddit instance")

    # get all of the files downloaded into the media folder
    flist0 = os.listdir(media_dir)
    saved_files = [f for f in flist0 if os.path.isfile(os.path.join(media_dir, f))]


    # check if any posts dont have a saved file should also check for postless media
    # idx = 0
    # while idx < len(old_posts):
    #     post = old_posts[idx]
    #     if not post.get_short_filename() in saved_files:
    #         old_posts.pop(idx)
    #         idx -= 1
    #     idx += 1

    # get saved posts (and upvoted?) ones for the database
    num_new_posts = scrape_posts(reddit, saved_files, scrape_amount, media_dir)
    

    # get all of the titles of the posts from the old saved posts
    # titles = []
    # for p in old_posts:
    #     titles.append(p.get_filename())

    # the new posts are those that do not have a matching title with the already saved posts
    # new_posts = [p for p in scraped_posts if not p.get_filename() in titles]




    print("Post info: old: {} | new: {} | total: {} | scraped: {}".format(1, 1, 1, num_new_posts))


    # save the posts
    # pickler.save(all_posts, posts_data_file)
