# media viewer


import numpy as np
import pandas as pd
import PySimpleGUI as sg
from PIL import Image, ImageTk
import os, io
import csv
import codecs
from numpy.random import default_rng
import random
from collections import Counter
import pickle
rng = default_rng()

# import build_csv_from_folder as csv_tools

import classes



# controls for gui
controls_next_post = ['MouseClick:Left', 'MouseWheel:Down', 'Up:38', 'Right:39', 'd', 'w', ' ', 'space:65', 'Right:114', 'Up:111', 'd:40', 'w:25']
controls_prev_post = ['MouseClick:Right', 'MouseWheel:Up', 'Down:40', 'Left:37', 'a', 's', 'Left:113', 'Down:116', 'a:38', 's:39']

controls_quit = [sg.WIN_CLOSED, 'Escape:27', 'Escape:9', 'Exit']

controls_shuffle_posts = ['Control_L:17', 'Control_L:37']

controls_inc_waittime = [']', 'bracketright:35']
controls_dec_waittime = ['[', 'bracketleft:34']

controls_new_suggested_tags = ['v', 'v:55']
controls_add_suggested_tags = ['z', 'x', 'c', 'z:52', 'x:53', 'c:54']
controls_add_suggested_tag_0 = ['z', 'z:52']
controls_add_suggested_tag_1 = ['x', 'x:53']

controls_group_selector = ['n', 'm', 'n:57', 'm:58']
controls_prev_group = ['n', 'n:57']

controls_remove_tag = ['r']
controls_view_next_tag = ['e']

controls_save_post_data = ['=', 'equal:21']

controls_toggle_groups = [',']
controls_toggle_slideshow = ['q']
controls_show_any_tagged = ['.']

# PIL supported image types
img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp", ".gif")

csv_header = ["filename", "ext", "title", "author", "subreddit", "waittime", "tags", "groups", "permalink", "url", "views", "timespent"]

# ------------------------------------------------------------------------------
# use PIL to read data of one image
# ------------------------------------------------------------------------------
def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    name, ext = os.path.splitext(f)
    if ext in img_types:
        print(ext)
        img = Image.open(f)
        img.thumbnail(maxsize)
        
        if first:                     # tkinter is inactive the first time
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            del img
            return bio.getvalue(), None
        return ImageTk.PhotoImage(img), img
    return None, None
# ------------------------------------------------------------------------------

# post key data
# 0			1	2		3		4			5			6		7		8			9					10
# Filename	ext	Title	Author	Subreddit	Waittime	Tags	Groups	Timestamp	Permalink (media)	URL (reddit post)


def pickle_posts(posts):
    with open(pickled_file, "wb") as f:
        pickle.dump(posts, f)

# slideshow controls
def next_idx(idx, total):
    idx += 1
    # if out of bounds
    if idx > total-1:
        idx = 0
    return idx

def prev_idx(idx, total):
    idx -= 1
    # if out of bounds
    if idx < 0:
        idx = total-1
    return idx


# top text displays most of the info
def get_top_text_string(post, idx, total_posts, group, view_group):
    string = "{} / {} posts\n{}".format(post_idx+1, total_posts, p.title)
    if p.author != "":
        string += "\nPosted by: {}".format(p.author)
    if p.subreddit != "":
        string += "\nIn: {}".format(p.subreddit)
    if view_group:
        string += "\nViewing Group: {}\nTags: {}\n".format(group.name, group.get_formatted_tags(format='row'))
    return string

def get_new_suggested_tag(tag_pool, shown_tags, post_tags):
    possible_tags = list(set(tag_pool).difference(set(post_tags)).difference(shown_tags))
    tag = ""
    if len(possible_tags) > 0:
        tag = random.choice(possible_tags)
    return tag

def get_all_new_suggested_tags(tag_pool, shown_tags, post_tags=[], amount=3):
    tags = []
    for i in range(amount):
        tags.append(get_new_suggested_tag(tag_pool, shown_tags, post_tags))
        shown_tags.append(tags[-1])
    return tags

def get_suggested_tag_text():
    return "\t\tz \t\tx \t\tc  \n\t\t{} \t\t{} \t\t{}".format(suggest_tags[0], suggest_tags[1], suggest_tags[2])

def get_posts_in_group(group, all_posts):
    posts = []
    for post in all_posts:
        a = set(post.tags)
        b = set(group.tags)
        intersect = list(a.intersection(b))
        if len(intersect) >= group.min_tags:
            posts.append(post)
            post.add_group(group.name)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_posts_with_tag(tag, all_posts):
    posts = []
    for post in all_posts:
        if tag in post.tags:
            posts.append(post)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_tagged_posts(all_posts, min_tags=0):
    posts = []
    for post in all_posts:
        if len(post.tags) > min_tags:
            posts.append(post)
    return posts


# Directory locations
#########################
saved_post_dir = "media/"
pickled_file = "posts.dat"

saved_post_dir = "reddit_media/"
pickled_file = "data/reddit_posts.dat"

data_dir = "data/saved/"

tags_file = "data/defaults/tags.dat"
groups_file = "data/defaults/groups.dat"

data = list()



with open(pickled_file, "rb") as f:
    data = pickle.load(f)

# get groups and tags
tags = []
groups = []

with open(tags_file, "rb") as f:
    tags = pickle.load(f)
with open(groups_file, "rb") as f:
    groups = pickle.load(f)


# make is so when you read data its saved here
# so on gifs that are bigger it doesnt hang up if you come back to it

read_img_data = []


# group idx is kinda fucky need to improve ui for group selector
group_idx = 0
tag_idx = 0

# post index is for the slideshow
post_idx = 0

# make a list of posts we want

#display_posts = get_posts_in_group(groups[group_idx], data)
#if len(display_posts) == 0:
#	group_idx += 1
#	display_posts = data[:,:]

display_posts = data

looped = False
shuffle_on_loop = True
total_posts = len(display_posts)

# pick these at random from list of not suggested tags
shown_tags = []
suggest_tags = get_all_new_suggested_tags(tags, shown_tags)
use_static_tags = False
static_tags = get_all_new_suggested_tags(tags, shown_tags)

showing_group = False
show_any_tagged = False


# shuffle the posts order, the rows
# print(display_posts)
if True:
    random.shuffle(display_posts)


# p is the current post
p = display_posts[post_idx]

g = groups[group_idx]
t = tags[tag_idx]

# waittime in ms
# mostly used for gif speed playback
# 30 is normal speed for most
waittime_idx = 6
waittimes = [1, 3, 6, 10, 15, 20, 30, 45, 60, 90, 120, 240]


cur_img = None

# get image data should be in the Post Class file
img_data, cur_img = get_img_data(p.get_filename(), first=True)


image_elem = sg.Image(data=img_data)

# make a class that constructs an image frame
# stack these together
# or make just the image elems tiled?

# gui elements

# tags, and suggest tags
tag_suggest_elem = sg.Text(get_suggested_tag_text(), font='22')
tag_select_elem_title = sg.Text("Tags: {} / {}".format(len(p.tags), len(tags)))
current_post_tags_elem = sg.Text(p.get_tags(format='col'), font='18')
tag_select_elem = []

for tag in tags:
    te = sg.Checkbox(str(tag))
    tag_select_elem.append(te)

top_text_elem = sg.Text(get_top_text_string(p, post_idx, total_posts, groups[group_idx], False))

extra_info_elem = sg.Text("Waittime: {}".format(waittimes[waittime_idx]))

bottom_elem = sg.ProgressBar(1, expand_x=True)

tag_browser_elem = sg.Text("Tag Browser")
group_select_elem = sg.Text("Group Select")

# define layout, show and read the form

# post_info_frame = [[filename_display_elem],
# 		[file_num_display_elem],
# 		[post_title_elem],
# 		[post_author_elem],
# 		[post_subreddit_elem],
# 		[post_tags_elem]]

# tag_frame = [[post_tags_elem],
# 		[suggested_tags_elem]]

# col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
            # [sg.Button('Next', size=(8, 2)), sg.Button('Prev', size=(8, 2)), file_num_display_elem]]

# layout = [[sg.Column(col_files), sg.Column(col)]]
# layout = [[sg.Column(img_col), sg.Column(post_info_col)]]

img_frame = [[top_text_elem],
            [tag_suggest_elem],
            [image_elem],
            [bottom_elem]]


tag_frame = [[tag_select_elem_title],
            [current_post_tags_elem]]

layout = [[sg.Column(img_frame), sg.Column(tag_frame)]]
# print(img_frame)
# print(tag_frame)

# print(layout)

window = sg.Window("Saved Post Viewer", layout, return_keyboard_events=True, auto_size_text=True,
                location=(0, 0), finalize=True, use_default_focus=True)

resave = False


view_group = False

changed_post = False


play_slideshow = False
slideshow_time = 0
slideshow_post_time = 2000

# for displaying posts, can add tag, view sets of posts, remove tag
while True:
    changed_post = False

    # read the window, this will wait for timeout, set to none to wait for input
    event, values = window.read(timeout=waittimes[waittime_idx])
    if not event == "__TIMEOUT__" and False:
        print(event, values)
    # Input Controls
    ##############################################
    # if user want to quit quit
    if event in controls_quit:
        break
    
    # increment post_idx
    elif event in controls_next_post:
        post_idx = next_idx(post_idx, len(display_posts))
        changed_post = True
        
    # decrement post_idx
    elif event in controls_prev_post:
        post_idx = prev_idx(post_idx, len(display_posts))
        changed_post = True
    
    # shuffle displayed posts and reset post_idx
    elif event in controls_shuffle_posts:
        rng.shuffle(display_posts)
        post_idx = 0
        changed_post = True

    # view group turn off, change name
    elif event in controls_toggle_groups:
        view_groups = False
        display_posts = data
        random.shuffle(display_posts)
        post_idx = 0
        changed_post = True

    # view any post that is tagged
    elif event in controls_show_any_tagged:
        if show_any_tagged:
            display_posts = data
        else:
            display_posts = get_tagged_posts(data)    
        random.shuffle(display_posts)
        show_any_tagged = not show_any_tagged
        post_idx = 0
        changed_post = True

    # group selector
    elif event in controls_group_selector:
        if event in controls_prev_group:
            group_idx -= 1
            if group_idx < 0:
                group_idx = len(groups)-1
        else:
            group_idx += 1
            if group_idx >= len(groups):
                group_idx = 0
        post_idx = 0
        g = groups[group_idx]
        display_posts = get_posts_in_group(g, data)
        random.shuffle(display_posts)
        changed_post = True

    # tag selector for viewing only a certain tag
    elif event in controls_view_next_tag:
        tag_idx += 1
        if tag_idx > len(tags):
            tag_idx = 0

        post_idx = 0
        t = tags[tag_idx]
        display_posts = get_posts_with_tag(t, data)
        random.shuffle(display_posts)
        changed_post = True
      


    # toggle the slideshow
    elif event in controls_toggle_slideshow:
        play_slideshow = not play_slideshow

    # change waittime
    elif event in controls_dec_waittime:
        waittime_idx = max(0, waittime_idx-1)
    elif event in controls_inc_waittime:
        waittime_idx = min(len(waittimes)-1, waittime_idx+1)

    # saving data, we want to save entire data set not just the displayed posts tho
    elif event in controls_save_post_data:
        pass

    # get a new set of tags, add old ones to shown tags
    elif event in controls_new_suggested_tags:
        shown_tags.append(suggest_tags[0])
        shown_tags.append(suggest_tags[1])
        shown_tags.append(suggest_tags[2])
        suggest_tags = get_all_new_suggested_tags(tags, shown_tags, p.tags)
        tag_suggest_elem.update(get_suggested_tag_text())
        slideshow_time = 0

    # add the tag to the post
    elif event in controls_add_suggested_tags:
        ti = 2
        if event in controls_add_suggested_tag_0:
            ti = 0
        elif event in controls_add_suggested_tag_1:
            ti = 1

        if suggest_tags[ti] != "":
            p.add_tag(suggest_tags[ti])
            # can make this stay the same 3 for quick selectiong many pictures
            suggest_tags[ti] = get_new_suggested_tag(tags, shown_tags, p.tags)

            # for now static suggested tags for quick tagging
            if use_static_tags:
                suggest_tags = static_tags

            resave = True
            
            tag_select_elem_title.update("Tags: {} / {}".format(len(p.tags), len(tags)))
            current_post_tags_elem.update(p.get_tags(format='col'))
            tag_suggest_elem.update(get_suggested_tag_text())
            slideshow_time = 0

    # removes the most recently added tag
    elif event in controls_remove_tag:
        if len(p.tags) > 0:
            p.remove_tag(p.tags[-1])

    # case where input occured but we dont do anything with
    else:
        pass

    # increment timer and go to next post if complete
    # can pause or reset if tagged and already next post
    if play_slideshow:
        slideshow_time += waittimes[waittime_idx]
        if changed_post:
            slideshow_time = 0
        bottom_elem.update(slideshow_time/slideshow_post_time)
        if slideshow_time > slideshow_post_time:
            slideshow_time = 0
            post_idx = next_idx(post_idx, len(display_posts))
            changed_post = True


    # local var for the current post
    # if we changed the post_idx get a new filename and update stuff
    if changed_post:
        # should this be a func? 
        p = display_posts[post_idx]
        img_data, cur_img = get_img_data(p.get_filename())
        shown_tags = []

        # could be a loop but we only have 3 anyways...
        suggest_tags = get_all_new_suggested_tags(tags, shown_tags, p.tags)
        
        # the update here should be a func since we update these values often minus top text
        top_text_elem.update(get_top_text_string(p, post_idx, len(display_posts), groups[group_idx], view_group))
        tag_select_elem_title.update("Tags: {} / {}".format(len(p.tags), len(tags)))
        current_post_tags_elem.update(p.get_tags(format='col'))
        tag_suggest_elem.update(get_suggested_tag_text())

    # check if looped and if so do stuff
    if looped:
        looped = False
        if shuffle_on_loop:
            display_posts = shuffle_posts(display_posts)

    # if a gif we need to update frame and draw
    if cur_img and p.ext == ".gif":
        # could do a progress bar for gifs
        frame = cur_img.tell() + 1
        if frame >= cur_img.n_frames:
            frame = 1
        if cur_img.n_frames != 1:
            cur_img.seek(frame)
        image_elem.update(data=ImageTk.PhotoImage(cur_img))
    else:
        image_elem.update(data=img_data)


window.close()

def view_post(posts, idx):
    p = posts[idx]
    

# if resave or True:
#     #data = display_posts
#     pickle_posts(data)

# Todo
###################
# list tags in a cleaner way
# way to make new tags
