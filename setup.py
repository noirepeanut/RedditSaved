import pickler
import classes
import os, io
import PySimpleGUI as sg

settings_file = 'data/settings.dat'


def load_settings():
    return settings

def main():
    slideshow_delay_range = (1, 120)
    default_slideshow_delay = 5000

    # controls for the browser (post displayer)
    default_controls = {
        
        'next_post' : ['f', ' '],
        'prev_post' : ['g'],

        'frame_select_up'     : ['w'],
        'frame_select_down'   : ['s'],
        'frame_select_left'   : ['a'],
        'frame_select_right'  : ['d'],

        'shuffle_posts' : ['y'],

        'view_next_group' : ['r'],
        'view_prev_group' : ['R'],
        
        'view_next_tag'   : ['e'],
        'view_prev_tag'   : ['E'],

        'new_suggested_tags'  : ['v'],
        'add_suggested_tag_0' : ['z'],
        'add_suggested_tag_1' : ['x'],
        'add_suggested_tag_2' : ['c'],

        'open_in_browser' : ['F1'],

        'remove_tag' : ['b'],
        'delete_post' : ['k'],

        'toggle_slideshow' : ['h'],
        
        'toggle_mute' : ['\t'],

        'inc_volume' : ['q'],
        'dec_volume' : ['Q'],

        'skip_ahead' : ['F'],
        'skip_back'  : ['G'],

        'toggle_pause' : ['S'],

        'view_all_posts'  : ['`'],
        'view_any_tagged' : ['.'],
        'view_not_tagged' : ['/'],
        'toggle_groups'   : [','],

        'view_subreddit'  : ['\''],
        'view_by_author'  : [';'],

        'view_newest_posts' : ['n'],
        'view_oldest_posts' : ['N'],

        'view_images_only' : ['<'],
        'view_gifs_only'   : ['>'],
        'view_videos_only' : ['?'],

        'add_temp_set_0' : ['0'],
        'add_temp_set_1' : ['1'],
        'add_temp_set_2' : ['2'],
        'add_temp_set_3' : ['3'],

        'view_temp_set_0' : [')'],
        'view_temp_set_1' : ['!'],
        'view_temp_set_2' : ['@'],
        'view_temp_set_3' : ['#'],

        'remove_temp_post' : ['t'],
        'clear_temp_set_0' : ['-'],
        'clear_temp_set_1' : ['7'],
        'clear_temp_set_2' : ['8'],
        'clear_temp_set_3' : ['9'],

        'move_temp_post_next' : ['D'],
        'move_temp_post_prev' : ['A'],

        'inc_waittime' : [']'],
        'dec_waittime' : ['['],

        'save_post_data' : ['='],
        'quit_program' : [sg.WIN_CLOSED, 'Exit', 'Escape']

    }

    # change temp sets to be 1 - 0 keys and shift of those
    # clear is when in the tempset like delete
    

    # initial default tags
    # not many so if you want to change its not difficult
    # but enough to organize posts
    default_tags = [
        "best",
        "cum", 
        "slut",
        "teen",
        "ass",
        "tits",
        "squirt",
        "bdsm",
        "blowjob",
        "doggy",
        "missionary",
        "pronebone",
        "riding"
    ]


    # inital groups

    # cum sluts, cum and slut both required
    cumslut_group = classes.Group("Cum Sluts", min_tags=2)
    cumslut_group.add_tags(["cum", "slut"])

    # sex group, any of doggy, missionary, pronebone, riding
    sex_group = classes.Group("Sex", min_tags=1)
    sex_group.add_tags(["doggy", "missionary", "pronebone", "riding"])
    sex_group.add_required_tag("sex")

    default_groups = [
        cumslut_group,
        sex_group
    ]


    # scrapper settings
    default_scrapper_config = {
        'username'      : "",
        'password'      : "",
        'client_id'     : "",
        'client_secret' : "",
        'scrape_amount' : 1000
    }


    # global settings
    default_settings = {
        'data_dir'                   : "data",
        'media_dir'                  : "reddit_media",
        'posts_data_file'            : "data/posts.dat",
        'tags_file'                  : "data/tags.dat",
        'groups_file'                : "data/groups.dat",
        'controls_file'              : "data/controls.dat",
        'scrapper_config_file'       : "data/scrapper_config.dat",
        'settings_file'              : "data/settings.dat",
        'tempsets_file'              : "data/tempsets.dat",
        'theme'                      : "Dark",
        'browser_theme'              : "Black",
        'view_reddit_info'           : True,
        'use_static_tags'            : False,
        'static_tags'                : ['teen', 'cum', 'slut'],
        'shuffle_on_startup'         : True,
        'shuffle_new_sets'           : True,
        'show_window_events'         : False,
        'clean_event'                : True,
        'window_size'                : (1900, 1000),
        'tag_group_window_size'      : (1200, 800),
        'min_media_size'             : (1000, 800),
        'max_media_size'             : (1600, 800),
        'force_media_size'           : False,
        'forced_media_size'          : (1200, 800),
        'background_color'           : 'black',
        'transparent_color'          : 'black',
        'start_muted'                : True,
        'filetypes'                  : ['.png', '.jpg', '.gif', '.mp4'],
        # 'right_click_menu_options' : [['next', 'maximize', 'minimize', 'play/pause', 'mute', 'quit']],
        'show_tag_sidebar'           : True,
        'save_tempsets'              : True,
        'slideshow_delay'            : 10,
        'layout_type'                : 'single',
        'save_reddit_info'           : True,
        'save_reddit_password'       : True
    }



    # load all of the stuff if they exist
    settings = pickler.load(settings_file, default_settings)
    tags = pickler.load(settings['tags_file'], default_tags)
    groups = pickler.load(settings['groups_file'], default_groups)
    controls = pickler.load(settings['controls_file'], default_controls)
    scrapper_config = pickler.load(settings['scrapper_config_file'], default_scrapper_config)


    # settings = default_settings

    sg.theme(settings['theme'])



    # username and password display
    username_text = ""
    password_text = ""
    client_id_text = ""
    client_secret_text = ""
    scrape_amount_text = "1000"
    if settings['save_reddit_info']:
        username_text = scrapper_config['username']
        client_id_text = scrapper_config['client_id']
        client_secret_text = scrapper_config['client_secret']
        scrape_amount_text = scrapper_config['scrape_amount']
    if settings['save_reddit_password']:
        password_text = scrapper_config['password']

    username_elem = sg.Input(username_text, key='_USERNAME_')
    password_elem = sg.Input(password_text, key='_PASSWORD_')
    client_id_elem = sg.Input(client_id_text, key='_CLIENT_ID_')
    client_secret_elem = sg.Input(client_secret_text, key='_CLIENT_SECRET_')
    scrape_amount_elem = sg.Input(scrape_amount_text, key='_SCRAPE_AMOUNT_')

    confirm_and_close_elem = sg.Button("Confirm and Close", key='_CONFIRM_AND_CLOSE_')
    close_no_save_elem = sg.Button("Close without saving", key='_CLOSE_NO_SAVE_')

    reddit_label_col = [
        [sg.Text("Username:")],
        [sg.Text("Password:")],
        [sg.Text("Client ID:")],
        [sg.Text("Client Secret:")],
        [sg.Text("Scrape Amount:")]
    ]

    reddit_input_col = [
        [username_elem],
        [password_elem],
        [client_id_elem],
        [client_secret_elem],
        [scrape_amount_elem]
    ]

    reddit_checkbox_col = [
        [sg.Checkbox("Save Reddit info", settings['save_reddit_info'], key='_SAVE_REDDIT_INFO_')],
        [sg.Checkbox("Save Reddit password", settings['save_reddit_password'], key='_SAVE_REDDIT_PASSWORD_')]
    ]

    reddit_frame = [
        [sg.Text("Input Reddit info:")],
        [sg.Column(reddit_label_col), sg.Column(reddit_input_col)], 
        [sg.Column(reddit_checkbox_col)]
    ]

    static_tag_inputs = [[sg.Input(t, key='_STATIC_TAG_{}_'.format(i))] for i, t in enumerate(settings['static_tags'])]

    

    slideshow_frame = [
        [sg.Checkbox("Show tag sidebar", settings['show_tag_sidebar'], key='_SHOW_TAG_SIDEBAR_')],
        [sg.Checkbox("View Reddit post info", settings['view_reddit_info'], key='_VIEW_REDDIT_INFO_')],
        [sg.Checkbox("Shuffle on startup", settings['shuffle_on_startup'], key='_SHUFFLE_ON_STARTUP_')],
        [sg.Checkbox("Shuffle new sets", settings['shuffle_new_sets'], key='_SHUFFLE_NEW_SETS_')],
        [sg.Checkbox("Show window events", settings['show_window_events'], key='_SHOW_WINDOW_EVENTS_')],
        [sg.Text("Theme:"), sg.Input(settings['theme'], key='_THEME_')],
        [sg.Text("Browser Theme:"), sg.Input(settings['browser_theme'], key='_BROWSER_THEME_')],
        [sg.Text("Slideshow delay: {} seconds".format(int(settings['slideshow_delay'])), key='_SLIDESHOW_DELAY_LABEL_')],
        [sg.Slider(range=slideshow_delay_range, default_value=settings['slideshow_delay'], key='_SLIDESHOW_DELAY_', orientation='h', resolution=1, enable_events=True)],
        [sg.Checkbox("Use static tags", settings['use_static_tags'], key='_USE_STATIC_TAGS_')],
        [sg.Text("Static tags:")],
        [sg.Column(static_tag_inputs)]
    ]

    import_frame = [
        [sg.Button("Import posts.dat", key='_IMPORT_POST_DATA_')],
        [sg.Input("import_dir/file.dat", key='_IMPORT_FILENAME_')],
    ]

    layout_view_frame = [
        [sg.Text("Set media layout\nsingle, 2side, 3side, 2stack, 3stack, 2x2, 3x3")],
        [sg.Input(settings['layout_type'], key='_LAYOUT_TYPE_')]
    ]

    reset_defaults_frame = [
        [sg.Text("Reset files?")],
        [sg.Button("Settings", key='_RESET_SETTINGS_', expand_x=True)],
        [sg.Button("Controls", key='_RESET_CONTROLS_', expand_x=True)],
        [sg.Button("Tags", key='_RESET_TAGS_', expand_x=True)],
        [sg.Button("Groups", key='_RESET_GROUPS_', expand_x=True)],
        [sg.Button("Posts", key='_RESET_POSTS_', expand_x=True)]
    ]

    filenames_label_col = [
        [sg.Text("posts.dat:", justification='right')],
        [sg.Text("tags.dat:", justification='right')],
        [sg.Text("groups.dat:", justification='right')],
        [sg.Text("Media save dir:", justification='right')],
    ]

    filenames_input_col = [
        [sg.Input("{}".format(settings['posts_data_file']), key='_FILENAME_POST_DATA_')],
        [sg.Input("{}".format(settings['tags_file']), key='_FILENAME_TAGS_')],
        [sg.Input("{}".format(settings['groups_file']), key='_FILENAME_GROUPS_')],
        [sg.Input("{}".format(settings['media_dir']), key='_MEDIA_DIR_')],

    ]

    filenames_frame = [
        [sg.Text("Change and set file names for data:")],
        [sg.Column(filenames_label_col), sg.Column(filenames_input_col)]

    ]


    scrapper_tab = sg.Tab("Reddit Scrapper", reddit_frame)
    slideshow_tab = sg.Tab("Media Browser", slideshow_frame)
    import_tab = sg.Tab("Import/Export", import_frame)
    filenames_tab = sg.Tab("Reset to defaults", reset_defaults_frame)
    reset_defaults_tab = sg.Tab("Change Filenames", filenames_frame)
    layout_view_tab = sg.Tab("Layouts", layout_view_frame)

    tabs_layout = [
        [slideshow_tab, layout_view_tab, scrapper_tab, filenames_tab, reset_defaults_tab, import_tab],
        [confirm_and_close_elem, close_no_save_elem]
    ]

    tab_group_elem = sg.TabGroup(tabs_layout)

    # layout = [
    #         [reddit_frame], 
    #         [slideshow_settings]
    # ]

    layout = [
        [tab_group_elem]
    ]


    window = sg.Window("Reddit Porn Scrapper and Browser Config", layout, return_keyboard_events=True)

    save_new_settings = False
    overwrite_tags = False
    overwrite_groups = False
    overwrite_controls = False


    while True:
        event, values = window.read(timeout=None)

        if event in (controls['quit_program'], '_CLOSE_NO_SAVE_', sg.WIN_CLOSED):

            break

        if event == '_CONFIRM_AND_CLOSE_':
            save_new_settings = True
            break

        # update elements
        if event == '_SLIDESHOW_DELAY_':
            window['_SLIDESHOW_DELAY_LABEL_'].update("Slideshow delay: {} seconds".format(int(values['_SLIDESHOW_DELAY_']/1000)))

        # so we need to update the ui when we reload setttings obviously
        # since after we load the ui data into the settings
        elif event == '_RESET_SETTINGS_':
            settings = default_settings
            window['_SHOW_TAG_SIDEBAR_'].update(settings['show_tag_sidebar'])
            window['_VIEW_REDDIT_INFO_'].update(settings['view_reddit_info'])
            window['_SHUFFLE_ON_STARTUP_'].update(settings['shuffle_on_startup'])
            window['_SHUFFLE_NEW_SETS_'].update(settings['shuffle_new_sets'])
            window['_SHOW_WINDOW_EVENTS_'].update(settings['show_window_events'])
            window['_THEME_'].update(settings['theme'])
            window['_BROWSER_THEME_'].update(settings['browser_theme'])
            window['_USE_STATIC_TAGS_'].update(settings['use_static_tags'])
            window['_SLIDESHOW_DELAY_'].update(settings['slideshow_delay'])
            window['_LAYOUT_TYPE_'].update(settings['layout_type'])
        elif event == '_RESET_TAGS_':
            tags = default_tags
            overwrite_tags = True
        elif event == '_RESET_GROUPS_':
            groups = default_groups
            overwrite_groups = True
        elif event == '_RESET_CONTROLS_':
            controls = default_controls
            overwrite_controls = True


    window.close()
    # print(event, values)
    # event, values = window.read()

    if save_new_settings:
        scrapper_config['username'] = window['_USERNAME_'].get()
        scrapper_config['password'] = window['_PASSWORD_'].get()
        scrapper_config['client_id'] = window['_CLIENT_ID_'].get()
        scrapper_config['client_secret'] = window['_CLIENT_SECRET_'].get()
        if type(int(window['_SCRAPE_AMOUNT_'].get())) == type(1):
            scrapper_config['scrape_amount'] = int(window['_SCRAPE_AMOUNT_'].get())

        settings['save_reddit_info'] = window['_SAVE_REDDIT_INFO_'].get()
        settings['save_reddit_password'] = window['_SAVE_REDDIT_PASSWORD_'].get()

        settings['show_tag_sidebar'] = window['_SHOW_TAG_SIDEBAR_'].get()
        settings['view_reddit_info'] = window['_VIEW_REDDIT_INFO_'].get()
        settings['shuffle_on_startup'] = window['_SHUFFLE_ON_STARTUP_'].get()
        settings['theme'] = window['_THEME_'].get()
        settings['browser_theme'] = window['_BROWSER_THEME_'].get()
        settings['show_window_events'] = window['_SHOW_WINDOW_EVENTS_'].get()

        # slideshow delay isnt working if you quit with escape
        # i mean escape shouldnt save data anyways so just save data

        if values['_SLIDESHOW_DELAY_']:
            settings['slideshow_delay'] = int(values['_SLIDESHOW_DELAY_'])

        settings['shuffle_new_sets'] = window['_SHUFFLE_NEW_SETS_'].get()
        settings['use_static_tags'] = window['_USE_STATIC_TAGS_'].get()

        settings['static_tags'] = [window['_STATIC_TAG_{}_'.format(x)].get() for x in range(len(settings['static_tags']))]

        settings['layout_type'] = window['_LAYOUT_TYPE_'].get()
        settings['posts_data_file'] = window['_FILENAME_POST_DATA_'].get()
        settings['tags_file'] = window['_FILENAME_TAGS_'].get()
        settings['groups_file'] = window['_FILENAME_GROUPS_'].get()
        settings['media_dir'] = window['_MEDIA_DIR_'].get()

    

    if not os.path.isdir(settings['data_dir']):
        os.mkdir(settings['data_dir'])
    if not os.path.isdir(settings['media_dir']):
        os.mkdir(settings['media_dir'])

    # do not overwrite tags, groups or controls if they already exist
    pickler.save(controls, settings['controls_file'], overwrite=overwrite_controls)
    pickler.save(tags, settings['tags_file'], overwrite=overwrite_tags)
    pickler.save(groups, settings['groups_file'], overwrite=overwrite_groups)

    # since we change settings and reddit scrapper settings here these files are overwritten
    pickler.save(scrapper_config, settings['scrapper_config_file'], overwrite=save_new_settings)
    pickler.save(settings, settings['settings_file'], overwrite=True)


if __name__ == '__main__':
    main()