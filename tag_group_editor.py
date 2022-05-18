import PySimpleGUI as sg
import codecs

import classes
import pickler



######### Functions

# format the tags for displaying
def format_tags(tags):
    s = ""
    for t in tags:
        s += t + "\n"
    return s

def format_groups(groups):
    s = ""
    for g in groups:
        s += g.get_formatted_info() + "\n"
    return s

def main():

    # if this filename changes we need to update for each file
    settings_file = 'data/settings.dat'
    settings = pickler.load(settings_file)

    group_count_values = [*range(1,10)]

    posts_data_file = settings['posts_data_file']
    tags_file = settings['tags_file']
    groups_file = settings['groups_file']
    controls_file = settings['controls_file']

    controls = pickler.load(controls_file)
    tags = pickler.load(tags_file)
    groups = pickler.load(groups_file)
    posts = []
    # posts = pickler.load(posts_data_file)

    group = None
    if len(groups) > 0:
        group = groups[0]


    ######## GUI SETUP
    sg.theme(settings['theme'])

    ######## TAG FRAME
    tag_entry_elem = sg.Input("", key="_TAG_ENTRY_")
    add_tag_elem = sg.Button("Add Tag", key="_NEW_TAG_")
    tag_remove_elem = sg.Button("Remove Tag", key="_REMOVE_TAG_")
    tag_display_elem = sg.Multiline(format_tags(tags), key="_TAG_DISPLAY_", expand_x=True, expand_y=True)


    ######## GROUP CREATE FRAME
    group_entry_elem = sg.Input("", key="_GROUP_ENTRY_")
    add_group_elem = sg.Button("Add Group", key="_NEW_GROUP_", size=(20,1))
    group_display_elem = sg.Multiline(format_groups(groups), key="_GROUP_DISPLAY_", expand_x=True, expand_y=True)
    group_count_elem = sg.Spin([*range(1,10)], initial_value=1, key="_GROUP_COUNT_", size=(3,2))


    ######## GROUP ADD TAG FRAME
    group_tag_entry_elem = sg.Input("", key="_GROUP_TAG_ENTRY_")
    group_add_tag_elem = sg.Button("Add Tag to Group", key="_NEW_GROUP_TAG_")
    group_add_required_tag_elem = sg.Button("Add Required Tag to Group", key="_NEW_GROUP_REQUIRED_TAG_")
    group_tag_display_elem = sg.Multiline("", key="_GROUP_TAG_DISPLAY_", expand_x=True, expand_y=True)
    group_selector = sg.Spin([*range(0,len(groups))], initial_value=0, key="_GROUP_SELECTOR_", size=(3,2), enable_events=True)
    current_group_elem = sg.Text(group.name)
    group_count_selector = sg.Spin([*range(0,10)], initial_value=1, key="_GROUP_COUNT_SELECTOR_", size=(3,2), enable_events=True)
    group_min_tags_elem = sg.Text("Min Tags:   ")


    ######## POST CLEANER FRAME
    clean_posts_tags_elem = sg.Button("Clean tags for posts", key="_CLEAN_TAGS_")

    ######## formatting the frames and their layouts
    tag_frame = [
        [sg.Text("Enter Tag:"), tag_entry_elem, add_tag_elem, tag_remove_elem],
        [tag_display_elem],
        [clean_posts_tags_elem]
    ]

    group_create_frame = [
        [sg.Text("Enter Group Name:"), group_entry_elem, add_group_elem],
        [sg.Text("Minimum Tags needed for Group:"), group_count_elem],
        [sg.Button("Delete Group", key='_DELETE_GROUP_')],
        [group_display_elem]
    ]

    group_tag_frame = [
        [sg.Text("Enter Tag for Group:"), group_tag_entry_elem, group_add_tag_elem, group_add_required_tag_elem],
        [group_selector, current_group_elem, group_min_tags_elem, group_count_selector],
        [group_tag_display_elem]
    ]




    # LAYOUT 2 top 1 bot
    tag_frame = sg.Frame("Tags", tag_frame, expand_y=True)
    group_create_frame = sg.Frame("Create Group", group_create_frame, expand_x=True, expand_y=True)
    group_tag_frame = sg.Frame("Group Tags", group_tag_frame, expand_x=True, expand_y=True)
    layout = [[tag_frame, group_create_frame], [group_tag_frame]]

    # LAYOUT 3 col
    # tag_frame = sg.Frame("Tags", tag_frame, expand_y=True)
    # group_create_frame = sg.Frame("Create Group", group_create_frame, expand_y=True)
    # group_tag_frame = sg.Frame("Group Tags", group_tag_frame, expand_y=True)
    # layout = [[tag_frame, group_create_frame, group_tag_frame]]


    # setup the window
    window = sg.Window("Tag and Group Editor", layout, return_keyboard_events=True, auto_size_text=True, use_default_focus=True, size=settings['tag_group_window_size'])


    ####### program loop
    while True:
        event, values = window.read(timeout=None)
        # print(event, values)
        if event in controls['quit_program']:
            # read the values in the entires and save them
            # since wed like to allow the user to delete lines of text
            break

        # how to differentiate when hitting enter to add either a tag or group?
        elif event in ("_NEW_TAG_", "\r"):
            t = tag_entry_elem.get()
            if t != "" and not t in tags:
                tags.append(t)
                tag_entry_elem.update("")
                tag_display_elem.update(format_tags(tags))

        elif event in ("_REMOVE_TAG_"):
            t = tag_entry_elem.get()
            if t != "" and t in tags:
                tags.remove(t)
                tag_entry_elem.update("")
                tag_display_elem.update(format_tags(tags))

        elif event in ("_DELETE_GROUP_"):
            g = group_entry_elem.get()
            group_names = [group.name for group in groups]
            if g != "" and g in group_names:
                remove_group = None
                for group in groups:
                    if g == group.name:
                        remove_group = group
                groups.remove(remove_group)
                group_entry_elem.update("")
                group_display_elem.update(format_groups(groups))

        elif event in ("_NEW_GROUP_"):
            g = group_entry_elem.get()
            if g != "" and not g in groups:
                g = classes.Group(g, group_count_elem.get())
                groups.append(g)
                group_entry_elem.update("")
                group_display_elem.update(format_groups(groups))
                group_selector.update(values=[*range(0,len(groups))])

        elif event in ("_NEW_GROUP_TAG_"):
            t = group_tag_entry_elem.get()
            group = groups[group_selector.get()]
            if t != "" and not t in group.tags:
                group.add_tag(t)
                group_tag_entry_elem.update("")
                group_tag_display_elem.update(group.get_formatted_tags(format='col'))
                group_display_elem.update(format_groups(groups))

        elif event in ("_NEW_GROUP_REQUIRED_TAG_"):
            t = group_tag_entry_elem.get()
            group = groups[group_selector.get()]
            if t != "" and not t in group.tags:
                group.add_required_tag(t)
                group_tag_entry_elem.update("")
                group_tag_display_elem.update(group.get_formatted_tags(format='col'))
                group_display_elem.update(format_groups(groups))

        elif event in ("_GROUP_SELECTOR_"):
            group = groups[group_selector.get()]
            group_tag_display_elem.update(group.get_formatted_tags(format='col'))
            current_group_elem.update(group.name)
            group_min_tags_elem.update("Min Tags: {}".format(group.min_tags))

        elif event in ("_GROUP_COUNT_SELECTOR_"):
            group = groups[group_selector.get()]
            group.set_min_tags(group_count_selector.get())
            group_min_tags_elem.update("Min Tags: {}".format(group.min_tags))

        elif event in ("_CLEAN_TAGS_"):
            for p in posts:
                for t in p.tags:
                    if not t in tags:
                        p.remove_tag(t)
            pickler.save(posts, posts_data_file)

    window.close()
    # before we quit save the data
    pickler.save(tags, tags_file)
    pickler.save(groups, groups_file)

if __name__ == '__main__':
    main()