# media viewer



import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageDraw
import webbrowser
import os, io
import codecs
import random
from collections import Counter
import pickle
import vlc
import copy
import time
from sys import platform as PLATFORM

import pickler
import classes

from models import Post, Tag, PostTag

inst = vlc.Instance('--no-xlib')
inst.log_unset()

# if this filename changes we need to update for each file
settings_file = 'data/settings.dat'

def clamp(num, min_value, max_value):
    num = max(min(num, max_value), min_value)
    return num

def get_timestep(lasttime):
    return time.time() - lasttime, time.time()

def view_temp_set(current_posts, temp_set, all_posts):
    if current_posts == temp_set:
        current_posts = all_posts
    elif len(temp_set) > 0:
        current_posts = temp_set
    return current_posts

def add_post_to_temp_set(post, temp_set):
    if post not in temp_set:
        # uncomment on relase, for my posts they are missing this var atm
        post.added_to_temp_set()
        temp_set.append(post)
    return temp_set

def add_suggest_tag(post, tag, tags, shown_tags):
    if tag != "":
        post.add_tag(tag)
        tag = get_new_suggested_tag(tags, shown_tags, post.tags)
    return tag

def clean_event(event):
    if type(event) == type("") and ":" in event:
        parts = event.split(":")
        event = parts[0]
    return event

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

def get_controls_label_text(controls):
    string = ""
    string += "Next post: {}".format(controls["next_post"])
    string += "\nPrev post: {}".format(controls["prev_post"])
    string += "\n"
    string += "\nNext group: {}".format(controls["view_next_group"])
    string += "\nPrev group: {}".format(controls["view_prev_group"])
    string += "\nNext tag: {}".format(controls["view_next_tag"])
    
    string += "\n"
    
    string += "\nView all tagged posts: {}".format(controls["view_any_tagged"])
    string += "\nView posts not tagged: {}".format(controls["view_not_tagged"])

    string += "\n"
    string += "\nSort by newest: {}".format(controls["view_newest_posts"])
    string += "\nSort by oldest: {}".format(controls["view_oldest_posts"])

    string += "\n"
    
    string += "\nToggle slideshow: {}".format(controls["toggle_slideshow"])
    string += "\nToggle mute: {}".format(controls["toggle_mute"])
    string += "\nIncrease volume: {}".format(controls["inc_volume"])
    string += "\nDecrease volume: {}".format(controls["dec_volume"])

    string += "\n"

    string += "\nSkip ahead 10%: {}".format(controls["skip_ahead"])
    string += "\nSkip back 10%: {}".format(controls["skip_back"])
    
    string += "\n"

    string += "\nShuffle posts {}".format(controls["shuffle_posts"])

    string += "\n"
    
    string += "\nAdd to temp set 1/2/3: {} / {} / {}".format(controls["add_temp_set_1"], controls["add_temp_set_2"], controls["add_temp_set_3"])
    string += "\nView   temp set 1/2/3: {} / {} / {}".format(controls["view_temp_set_1"], controls["view_temp_set_2"], controls["view_temp_set_3"])
    string += "\nClear  temp set 1/2/3: {} / {} / {}".format(controls["clear_temp_set_1"], controls["clear_temp_set_2"], controls["clear_temp_set_3"])

    string += "\n"
    
    string += "\nRemove last tag: {}".format(controls["remove_tag"])
    string += "\nRemove post from current temp set: {}".format(controls["remove_temp_post"])
    string += "\nDelete post: {}".format(controls["delete_post"])


    string = string.replace('\'', '').replace('[', '').replace(']', '')

    return string

# top text displays most of the info
def get_top_text_string(post, idx, total_posts, show_reddit_info=False):
    # string = "{}".format(post.title)
    # make the title have a make length of line
    # do this by splitting all the words
    # then adding each word one by one to the title string
    # when the title string > max line length add new line

    string = ""
    title_words = post.title.split(" ")
    max_title_line_length = 40
    cur_line_length = 0
    for word in title_words:
        if cur_line_length > max_title_line_length:
            string += "\n"
            cur_line_length = 0
        string += word + " "
        cur_line_length += len(word)

    string += "\n"

    if show_reddit_info:
        if post.author != "":
            string += "\nPosted by: {}".format(post.author)
        if post.subreddit != "":
            string += "\nIn: {}".format(post.subreddit)
    
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
    return "z\t\tx\t\tc  \n{}\t\t{}\t\t{}".format(suggest_tags[0], suggest_tags[1], suggest_tags[2])

def get_posts_in_group(group, all_posts):
    posts = []
    for post in all_posts:
        a = set(post.tags)
        b = set(group.tags)
        c = set(group.required_tags)
        required = list(a.intersection(c))
        intersect = list(a.intersection(b))
        if len(intersect) >= group.min_tags and len(required) == len(group.required_tags):
            posts.append(post)
            post.add_group(group.name)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_all_images(all_posts):
    posts = []
    for post in all_posts:
        if post.is_image():
            posts.append(post)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_all_gifs(all_posts):
    posts = []
    for post in all_posts:
        if post.is_gif():
            posts.append(post)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_all_videos(all_posts):
    posts = []
    for post in all_posts:
        if post.is_video():
            posts.append(post)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_posts_not_viewed(all_posts):
    posts = []
    for post in all_posts:
        if post.views == 0:
            posts.append(post)
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

def get_untagged_posts(all_posts):
    posts = []
    for post in all_posts:
        if len(post.tags) == 0:
            posts.append(post)
    if len(posts) == 0:
        posts = all_posts
    return posts

def get_tagged_posts(all_posts, min_tags=0):
    posts = []
    for post in all_posts:
        if len(post.tags) > min_tags:
            posts.append(post)
    if len(posts) == 0:
        posts = all_posts
    return posts

def new_sort(p):
    return p.get_idx()

def view_sort(p):
    return p.get_views()

def get_posts_sorted_newest(posts):
    posts.sort(reverse=True, key=new_sort)

    return posts

def get_posts_sorted_oldest(posts):
    posts.sort(reverse=False, key=new_sort)
    return posts

def clear_frame_titles():
    for y in range(media_layout[1]):
        for x in range(media_layout[0]):
            window["_FRAME_{}_{}_".format(x, y)].update(" ")

def get_set_name(cur_set, view_dict, group, tag, temp_set_idx):
    set_name = view_dict[cur_set]
    set_name += "\n"

    if cur_set == 'by_tag':
        set_name += "Viewing tag: {}".format(tag)
    elif cur_set == 'by_group':
        set_name += "Viewing group: {}\nTags: {}".format(group.name, group.get_formatted_tags(format='row'))
    elif cur_set == 'temp_set':
        set_name += "Viewing temp set {}".format(temp_set_idx)
    elif cur_set == 'not_tagged':
        set_name += ""
    elif cur_set == 'any_tagged':
        set_name += ""

    return set_name

def new_media_frame(x, y, media_data=None):
    layout = [
        [sg.Text("", key='_SET_INFO_{}{}_'.format(x,y), justification='center')],
        [sg.Text("", key='_TITLE_{}{}_'.format(x,y), font=('Helvetica 20'), justification='center')],
        [sg.ProgressBar(max_value=1, orientation="horizontal", bar_color=("white", "grey"),  key='_PROGRESS_{}{}_'.format(x,y), expand_x=False)],
        [sg.Image(data=media_data,  key='_MEDIA_{}{}_'.format(x,y), expand_x=True, size=(1600, 800))],
        # [sg.Text("", key='_TAG_HEADER_{}{}_'.format(x,y), justification='center', expand_x=False)],
        # [sg.Text("", key='_POST_TAGS_{}{}_'.format(x,y), font='18', justification='left')]
    ]
    layout = [[sg.Column(layout, element_justification='center')]]
    player = inst.media_player_new()
    frame = {
        'index'  : f'{x}{y}',
        'layout' : sg.Column(layout),
        'player' : player
    }
    return frame


def main():
    settings = pickler.load(settings_file)
    view_reddit_info = settings['view_reddit_info']



    saved_post_dir = settings['media_dir']
    data_dir = settings['data_dir']


    posts_data_file = settings['posts_data_file']
    tags_file = settings['tags_file']
    groups_file = settings['groups_file']
    controls_file = settings['controls_file']



    sg.theme(settings['browser_theme'])





    # load data
    tags = pickler.load(tags_file)
    groups = pickler.load(groups_file)
    data = pickler.load(posts_data_file)
    controls = pickler.load(controls_file)





    # group idx is kinda fucky need to improve ui for group selector
    group_idx = 0
    tag_idx = 0

    # post index is for the slideshow
    post_idx = 0
    temp_set_idx = 0


    # temp sets for adding posts to temprarily, they are deleted on exit
    temp_sets = [[],[],[],[]]

    if settings['save_tempsets']:
        temp_sets = pickler.load(settings['tempsets_file'], temp_sets)

    # types of sets we can be viewing, need a better name for this or data structure
    set_views = {
        'all' : 'all posts',
        'any_tagged' : 'any tagged',
        'not_tagged' : 'not tagged',
        'by_tag' : 'by tag',
        'by_group' : 'by group',
        'temp_set' : 'temp set',
        'sorted_newest' : 'newest first',
        'sorted_oldest' : 'oldest first',
        'images_only' : 'images only',
        'gifs_only' : 'gifs only',
        'videos_only' : 'videos only',
        'exited_posts' : 'exited_posts',
    }

    # set_views = ('any', 'all_tagged', 'not_tagged', 'by_tag', 'by_group', 'temp_set')
    current_set = 0
    cur_set_view = 'all'


    # set the display_posts to be all of the data
    display_posts = data

    media_data = None

    # loop is when viewed_posts is around total_posts
    shuffle_on_loop = False
    viewed_posts = 0
    total_posts = len(display_posts)

    # pick these at random from list of not suggested tags
    shown_tags = []
    suggest_tags = get_all_new_suggested_tags(tags, shown_tags)
    use_static_tags = settings['use_static_tags']
    static_tags = settings['static_tags']


    # shuffle the posts order, the rows
    if settings['shuffle_on_startup']:
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

    lasttime = time.time()
    timestep = 0

    # the test post is so the imagetk can be setup and initialized properly
    test_post = random.choice(display_posts)
    while not test_post.is_image():
        test_post = random.choice(display_posts)
    # the stuff to init imagetk
    img = Image.open(test_post.get_filename())
    img.thumbnail((1000, 600))
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    bio_value = bio.getvalue()


    players = []

    # gui elements
    media_layout = (1,1)
    if settings['layout_type'] == 'single':
        media_layout = (1,1)
    elif settings['layout_type'] == '2side':
        media_layout = (2,1)
    elif settings['layout_type'] == '3side':
        media_layout = (3,1)
    elif settings['layout_type'] == '2stack':
        media_layout = (1,2)
    elif settings['layout_type'] == '3stack':
        media_layout = (1,3)
    elif settings['layout_type'] == '2x2':
        media_layout = (2,2)
    elif settings['layout_type'] == '3x3':
        media_layout = (3,3)



    frame_selector = classes.Frame_Selector(layout_shape=media_layout)

    media_frames = []

    default_frame_size = (1600, 800)
    default_media_size = (1200, 700)
    frame_width = default_frame_size[0]/media_layout[0]
    frame_height = default_frame_size[1]/media_layout[1]
    frame_size = (int(frame_width), int(frame_height))

    media_layouts = [[f'{x}{y}' for x in range(frame_selector.wide)] for y in range(frame_selector.high)]
    # print(media_layouts)

    for x in range(media_layout[0]):
        for y in range(media_layout[1]):
            frame = new_media_frame(x+1, y+1, bio_value)
            media_frames.append(frame['layout'])
            players.append(frame['player'])
            media_layouts[y][x] = frame['layout']
            # print(media_layouts)


    # get_top_text_string(p, post_idx, total_posts)





    # these are static for all posts and all layouts
    tag_suggest_elem = sg.Table([suggest_tags], headings=['z', 'x', 'c'], key='_TAG_SUGGEST_', justification='center', max_col_width=30, def_col_width=20,
                                auto_size_columns=False, font='20', 
                                hide_vertical_scroll=True, select_mode=sg.TABLE_SELECT_MODE_NONE, row_height=2)


    # media_elem = sg.Image(data=media_data, size=(500,300), key="_MEDIA_")

    # add these to the media frame?
    post_tags_header_elem = sg.Text("Tags: {} / {}".format(len(p.tags), len(tags)), key='_TAG_HEADER_', justification='center', expand_x=False)
    post_tags_elem = sg.Text(p.get_tags(format='col'), font='18', key='_POST_TAGS_', justification='left')


    controls_display_elem = sg.Text("{}".format(get_controls_label_text(controls)), key='_CONTROLS_DISPLAY_', justification='left', expand_x=True)


    # print(get_controls_label_text(controls))

    # define layout, show and read the form

    controls_frame = [
        [sg.vbottom(controls_display_elem)]
    ]

    tag_frame = [
        [post_tags_header_elem],
        [post_tags_elem]
    ]

    # main_frame = [
    #     [post_text_elem],
    #     [set_info_elem],
    #     [media_elem],
    #     [tag_suggest_elem],
    # ]
    layout = [
            [tag_suggest_elem],
            [
                # sg.vtop(sg.Column(controls_frame, vertical_alignment='bottom', justification='left')), 
                sg.Column(media_layouts, vertical_alignment='center', justification='center'),
                sg.Column(tag_frame, vertical_alignment='top', visible=settings['show_tag_sidebar'])
            ]
        ]

    layout = [
        [
            sg.vtop(sg.Column(controls_frame, vertical_alignment='bottom', justification='left'), expand_x=False),
            sg.Column(layout, element_justification='center', expand_x=True)
        ]
    ]

    # layout = [[sg.Column(media_layouts, vertical_alignment='center', justification='center', element_justification='center')]]


    window = sg.Window("Saved Post Viewer", layout, return_keyboard_events=True, 
        background_color=settings['background_color'],
        # transparent_color=settings['transparent_color'], 
        # no_titlebar=True,
        resizable=True,
        # right_click_menu_tearoff=True,
        # right_click_menu=settings['right_click_menu_options'],
        # location=(0,0),
        element_justification='center',
        element_padding=(0,0), 
        grab_anywhere=True, grab_anywhere_using_control=False, 
        size=settings['window_size'],
        auto_size_text=True, 
        finalize=True,
        use_default_focus=True 
        )

    resave = False


    # cant grab the video to move it



    window.force_focus()


    view_group = False

    changed_post = False



    play_slideshow = False
    slideshow_time = 0
    slideshow_delay = settings['slideshow_delay']

    # vlc stuff for playing videos
    
    player_idx = 0

    

    frame_x, frame_y = 1, 1
    for player in players:
        player.audio_set_mute(settings['start_muted'])
        if PLATFORM.startswith('linux'):
            player.set_xwindow(window[frame_selector.get_key_at('MEDIA', frame_x, frame_y)].Widget.winfo_id())
        else:
            player.set_hwnd(window[frame_selector.get_key_at('MEDIA', frame_x, frame_y)].Widget.winfo_id())
        frame_x += 1
        if frame_x > frame_selector.wide:
            frame_x = 1
            frame_y += 1


    frame_x, frame_y = 1, 1
    for i in range(frame_selector.size):
        media_data = p.get_media()
        if p.is_image() or p.is_gif():
            window[frame_selector.get_key_at('MEDIA', frame_x, frame_y)].update(data=media_data)
        elif p.is_video():
            players[i].set_mrl(p.get_filename())
        frame_x += 1
        if frame_x > frame_selector.wide:
            frame_x = 1
            frame_y += 1
        viewed_posts += 1
        post_idx += 1
        p = display_posts[post_idx]


    # for displaying posts, can add tag, view sets of posts, remove tag
    while True:
        changed_post = False

        # read the window, this will wait for timeout, set to none to wait for input
        event, values = window.read(timeout=waittimes[waittime_idx])
        if settings['clean_event']:
            event = clean_event(event)
        if not event == "__TIMEOUT__" and settings['show_window_events']:
            print(event, values)
        # Input Controls
        ##############################################
        # if user want to quit quit
        if event in controls['quit_program']:
            break
        
        # increment post_idx
        elif event in controls['next_post']:
            post_idx = next_idx(post_idx, len(display_posts))
            changed_post = True
            
        # decrement post_idx
        elif event in controls['prev_post']:
            post_idx = prev_idx(post_idx, len(display_posts))
            changed_post = True
        
        # frame selector movement
        elif event in controls['frame_select_up']:
            frame_selector.up()
        elif event in controls['frame_select_down']:
            frame_selector.down()
        elif event in controls['frame_select_left']:
            frame_selector.left()
        elif event in controls['frame_select_right']:
            frame_selector.right()

        # shuffle displayed posts and reset post_idx
        elif event in controls['shuffle_posts']:
            change_set(shuffle=True)

        # view group turn off, change name
        elif event in controls['toggle_groups']:
            cur_set_view = 'all'
            display_posts = data
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)

        # view any post that is tagged
        elif event in controls['view_any_tagged']:
            if cur_set_view == 'any_tagged':
                display_posts = data
                cur_set_view = 'all'
            else:
                display_posts = get_tagged_posts(data)
                cur_set_view = 'any_tagged'
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)

        # view any post not tagged
        elif event in controls['view_not_tagged']:
            untagged = get_untagged_posts(data)
            if display_posts == untagged:
                display_posts = data
                cur_set_view = 'all'
            else:
                display_posts = untagged
                cur_set_view = 'not_tagged'
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)

        # view posts sorted by newest first
        elif event in controls['view_newest_posts']:
            display_posts = get_posts_sorted_newest(display_posts)
            changed_post = True
            cur_set_view = 'sorted_newest'
            post_idx = 0
            
        # view posts sorted by oldest first
        elif event in controls['view_oldest_posts']:
            display_posts = get_posts_sorted_oldest(display_posts)
            changed_post = True
            cur_set_view = 'sorted_oldest'
            post_idx = 0

        # view only images
        elif event in controls['view_images_only']:
            display_posts = get_all_images(data)
            changed_post = True
            cur_set_view = 'images_only'
            post_idx = 0

        # view only gifs
        elif event in controls['view_gifs_only']:
            display_posts = get_all_gifs(data)
            changed_post = True
            cur_set_view = 'gifs_only'
            post_idx = 0

        # view only videos
        elif event in controls['view_videos_only']:
            display_posts = get_all_videos(data)
            changed_post = True
            cur_set_view = 'videos_only'
            post_idx = 0

        # group selector
        elif event in controls['view_next_group']:
            group_idx += 1
            if group_idx >= len(groups):
                group_idx = 0
            cur_set_view = 'by_group'
            g = groups[group_idx]
            display_posts = get_posts_in_group(g, data)
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)


        elif event in controls['view_prev_group']:
            group_idx -= 1
            if group_idx < 0:
                group_idx = len(groups)-1
            cur_set_view = 'by_group'
            g = groups[group_idx]
            display_posts = get_posts_in_group(g, data)
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)

            
        # tag selector for viewing only a certain tag
        elif event in controls['view_next_tag']:
            tag_idx += 1
            if tag_idx > len(tags):
                tag_idx = 0
            t = tags[tag_idx]
            cur_set_view = 'by_tag'
            display_posts = get_posts_with_tag(t, data)
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)


        elif event in controls['view_prev_tag']:
            tag_idx -= 1
            if tag_idx < 0:
                tag_idx = len(tags)-1
            cur_set_view = 'by_tag'
            t = tags[tag_idx]
            display_posts = get_posts_with_tag(t, data)
            changed_post = True
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)

        elif event in controls['toggle_pause']:
            for player in players:
                players[frame_selector.get_idx()].pause()
            
        elif event in controls['toggle_mute']:
            for player in players:
                player.audio_toggle_mute()

        elif event in controls['inc_volume']:
            for player in players:
                cur_vol = player.audio_get_volume() + 10
                cur_vol = clamp(cur_vol, 0, 100)
                player.audio_set_mute(False)
                player.audio_set_volume(cur_vol)


        elif event in controls['dec_volume']:
            for player in players:
                cur_vol = player.audio_get_volume() - 10
                cur_vol = clamp(cur_vol, 0, 100)
                player.audio_set_mute(False)
                player.audio_set_volume(cur_vol)

        elif event in controls['skip_ahead']:
            for player in players:
                cur_pos = player.get_position() + 0.1
                if cur_pos > 1:
                    cur_pos -= 1
                player.set_position(cur_pos)

        elif event in controls['skip_back']:
            for player in players:
                cur_pos = player.get_position() - 0.1
                if cur_pos < 0:
                    cur_pos += 1
                player.set_position(cur_pos)

        elif event in controls['view_all_posts']:
            display_posts = data
            changed_post = True
            cur_set_view = 'all'
            post_idx = 0
            if settings['shuffle_new_sets']:
                random.shuffle(display_posts)


        elif event in controls['add_temp_set_0']:
            temp_sets[0] = add_post_to_temp_set(p, temp_sets[0])

        elif event in controls['add_temp_set_1']:
            temp_sets[1] = add_post_to_temp_set(p, temp_sets[1])

        elif event in controls['add_temp_set_2']:
            temp_sets[2] = add_post_to_temp_set(p, temp_sets[2])

        elif event in controls['add_temp_set_3']:
            temp_sets[3] = add_post_to_temp_set(p, temp_sets[3])

        elif event in controls['view_temp_set_0']:
            temp_set_idx = 0
            changed_post = True
            post_idx = 0
            display_posts = view_temp_set(display_posts, temp_sets[temp_set_idx], data)
            cur_set_view = 'temp_set'
        
        elif event in controls['view_temp_set_1']:
            temp_set_idx = 1
            changed_post = True
            post_idx = 0
            display_posts = view_temp_set(display_posts, temp_sets[temp_set_idx], data)
            cur_set_view = 'temp_set'

        elif event in controls['view_temp_set_2']:
            temp_set_idx = 2
            changed_post = True
            post_idx = 0
            display_posts = view_temp_set(display_posts, temp_sets[temp_set_idx], data)
            cur_set_view = 'temp_set'

        elif event in controls['view_temp_set_3']:
            temp_set_idx = 3
            changed_post = True
            post_idx = 0
            display_posts = view_temp_set(display_posts, temp_sets[temp_set_idx], data)
            cur_set_view = 'temp_set'

        elif event in controls['clear_temp_set_0']:
            temp_sets[0] = []

        elif event in controls['clear_temp_set_1']:
            temp_sets[1] = []

        elif event in controls['clear_temp_set_2']:
            temp_sets[2] = []

        elif event in controls['clear_temp_set_3']:
            temp_sets[3] = []
    

        elif event in controls['remove_temp_post']:
            if cur_set_view == 'temp_set':

                del temp_sets[temp_set_idx][post_idx]
                # post_idx -= 1
                if post_idx >= len(display_posts):
                    post_idx = 0
                changed_post = True
            
        elif event in controls['move_temp_post_next']:
            if cur_set_view == 'temp_set':
                pa = temp_sets[temp_set_idx].pop(post_idx)
                pb = temp_sets[temp_set_idx].pop(min(post_idx,len(display_posts)-1))
                temp_sets[temp_set_idx].insert(post_idx, pb)
                post_idx = post_idx + 1
                if post_idx > len(display_posts):
                    post_idx = 0
                temp_sets[temp_set_idx].insert(post_idx, pa)
                changed_post = True

        elif event in controls['move_temp_post_prev']:
            if cur_set_view == 'temp_set':
                pa = temp_sets[temp_set_idx].pop(post_idx)
                pb = temp_sets[temp_set_idx].pop(post_idx-1)
                temp_sets[temp_set_idx].insert(post_idx, pb)
                post_idx = post_idx - 1
                if post_idx < 0:
                    post_idx = len(display_posts) 
                temp_sets[temp_set_idx].insert(post_idx, pa)
                changed_post = True


        # toggle the slideshow
        elif event in controls['toggle_slideshow']:
            play_slideshow = not play_slideshow

        # change waittime
        elif event in controls['dec_waittime']:
            waittime_idx = max(0, waittime_idx-1)
        elif event in controls['inc_waittime']:
            waittime_idx = min(len(waittimes)-1, waittime_idx+1)

        # saving data, we want to save entire data set not just the displayed posts tho
        elif event in controls['save_post_data']:
            pickler.save(data, posts_data_file)
            print("saved post data")

        # get a new set of tags, add old ones to shown tags
        elif event in controls['new_suggested_tags']:
            shown_tags.append(suggest_tags[0])
            shown_tags.append(suggest_tags[1])
            shown_tags.append(suggest_tags[2])
            suggest_tags = get_all_new_suggested_tags(tags, shown_tags, p.tags)
            window['_TAG_SUGGEST_'].update([suggest_tags])
            slideshow_time -= 2

        # add the tag to the post
        elif event in controls['add_suggested_tag_0']:
            suggest_tags[0] = add_suggest_tag(p, suggest_tags[0], tags, shown_tags)
            window['_TAG_SUGGEST_'].update([suggest_tags])
            window['_TAG_HEADER_'].update("Tags: {} / {}".format(len(p.tags), len(tags)))
            window['_POST_TAGS_'].update(p.get_tags(format='col'))
            window['_TAG_SUGGEST_'].update([suggest_tags])
            slideshow_time -= 2

        # add the tag to the post
        elif event in controls['add_suggested_tag_1']:
            suggest_tags[1] = add_suggest_tag(p, suggest_tags[1], tags, shown_tags)
            window['_TAG_SUGGEST_'].update([suggest_tags])
            window['_TAG_HEADER_'].update("Tags: {} / {}".format(len(p.tags), len(tags)))
            window['_POST_TAGS_'].update(p.get_tags(format='col'))
            window['_TAG_SUGGEST_'].update([suggest_tags])
            slideshow_time -= 2

        # add the tag to the post
        elif event in controls['add_suggested_tag_2']:
            suggest_tags[2] = add_suggest_tag(p, suggest_tags[2], tags, shown_tags)
            window['_TAG_SUGGEST_'].update([suggest_tags])
            window['_TAG_HEADER_'].update("Tags: {} / {}".format(len(p.tags), len(tags)))
            window['_POST_TAGS_'].update(p.get_tags(format='col'))
            window['_TAG_SUGGEST_'].update([suggest_tags])
            slideshow_time -= 2

        # removes the most recently added tag
        elif event in controls['remove_tag']:
            if len(p.tags) > 0:
                p.remove_tag(p.tags[-1])
                window['_POST_TAGS_'].update(p.get_tags(format='col'))


        # elif event in controls['ignore_post']:
        #     p.ignore = True

        elif event in controls['delete_post']:
            data.remove(p)
            post_idx = next_idx(post_idx, len(display_posts))
            changed_post = True

        elif event in controls['open_in_browser']:
            webbrowser.open('www.reddit.com{}'.format(p.permalink))
        


        # case where input occured but we dont do anything with
        else:
            pass

        # increment timer and go to next post if complete
        # can pause or reset if tagged and already next post
        if play_slideshow:
            # slideshow_time += waittimes[waittime_idx]
            timestep, lasttime = get_timestep(lasttime)
            slideshow_time += timestep
            #print("{} / {}, + {}".format(slideshow_time, slideshow_delay, timestep))
            if changed_post:
                slideshow_time = 0
            if slideshow_time > slideshow_delay:
                slideshow_time = 0
                post_idx = next_idx(post_idx, len(display_posts))
                changed_post = True


        # local var for the current post
        # if we changed the post_idx get a new filename and update stuff
        if changed_post:
            viewed_posts += 1
            p = display_posts[post_idx]
            media_data = p.get_media()

            p.viewed()
            # print(p.get_idx())

            # p.add_time_viewed(time)
            
            # print(p.get_short_filename())
            
            if p.is_image() or p.is_gif():
                players[frame_selector.get_idx()].stop()
            if p.is_video():
                players[frame_selector.get_idx()].set_mrl(p.get_filename())
                players[frame_selector.get_idx()].play()

            shown_tags = []
            suggest_tags = get_all_new_suggested_tags(tags, shown_tags, p.tags)
            
            window[frame_selector.get_key('TITLE')].update(get_top_text_string(p, post_idx, len(display_posts)))
            window[frame_selector.get_key('SET_INFO')].update("{} / {} posts in current set: {}".format(post_idx+1, len(display_posts), get_set_name(cur_set_view, set_views, g, t, temp_set_idx)))
            window['_TAG_HEADER_'].update("Tags: {} / {}".format(len(p.tags), len(tags)))
            window['_POST_TAGS_'].update(p.get_tags(format='col'))
            window['_TAG_SUGGEST_'].update([suggest_tags])


            # check if looped and if so do stuff
            if shuffle_on_loop and viewed_posts % total_posts == 0:
                display_posts = shuffle_posts(display_posts)

            # if a gif we need to update frame and draw

            if window[frame_selector.get_key('MEDIA')].get_size() < settings['min_media_size']:
                window[frame_selector.get_key('MEDIA')].set_size(settings['min_media_size'])
            if window[frame_selector.get_key('MEDIA')].get_size() > settings['max_media_size']:
                window[frame_selector.get_key('MEDIA')].set_size(settings['max_media_size'])

            if settings['force_media_size']:
                window[frame_selector.get_key('MEDIA')].set_size(settings['forced_media_size'])
            
            if p.is_image():
                window[frame_selector.get_key('MEDIA')].update(data=media_data)
                window[frame_selector.get_key('PROGRESS')].update(current_count=0, visible=False)

            if p.is_gif():
                window[frame_selector.get_key('MEDIA')].update(data=media_data)
                window[frame_selector.get_key('PROGRESS')].update(current_count=0, visible=True)

         


        if p.is_gif():
            media_data = p.get_media()
            # print(img.tell())
            # print(list(p.cur_img.getdata(0)))
            window[frame_selector.get_key('PROGRESS')].update(current_count=p.frame_idx, max=p.n_frames, visible=True)
            window[frame_selector.get_key('MEDIA')].update(data=media_data)
            # window[frame_selector.get_key('MEDIA')].update(data=ImageTk.PhotoImage(img))
            # window.refresh()
            # window[frame_selector.get_key('MEDIA')].update_animation_no_buffering(p.get_filename())

        if p.is_video():

            window[frame_selector.get_key('PROGRESS')].update(current_count=players[frame_selector.get_idx()].get_position(), max=1, visible=True)    
            # print(players[frame_selector.get_idx()].get_position())
            if not players[frame_selector.get_idx()].is_playing() and players[frame_selector.get_idx()].get_position() >= 0.97:
                players[frame_selector.get_idx()].set_mrl(p.get_filename())
                players[frame_selector.get_idx()].play()
        # frame_x, frame_y = 1, 1
        # for i in range(frame_selector.size):
        #     if p.is_gif():
        #         media_data = p.get_media()
        #         window[frame_selector.get_key_at('MEDIA', frame_x, frame_y)].update(data=media_data)
        #     elif p.is_video():
        #         pass
        #         # players[i].set_mrl(p.get_filename())
        #     frame_x += 1
        #     if frame_x > frame_selector.wide:
        #         frame_x = 1
        #         frame_y += 1
        #     viewed_posts += 1
        #     post_idx += 1
        #     p = display_posts[post_idx]
        

            


    window.close()
    
    


    # unload all of the image data from the post so the file isnt so large
    for post in data:
        if post.loaded:
            post.unload_image()

    # not working as attribute wasnt set for my file
    p.exited_post()

    pickler.save(data, posts_data_file)

    if settings['save_tempsets']:
        for temp_set in temp_sets:
            for post in temp_set:
                if post.loaded:
                    post.unload_image()
        pickler.save(temp_sets, settings['tempsets_file'])

if __name__ == '__main__':
    main()
