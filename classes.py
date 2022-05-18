# classes in here
import os
from PIL import Image, ImageTk
import PySimpleGUI as sg



replace_chars = ['[', ']', '(', ')']

reddit_home_url = 'https://www.reddit.com'
saved_dir = "saved_posts/"
temp_dir = "temp/"

image_filetypes = (".png", ".jpg", "jpeg", ".tiff", ".bmp")
video_filetypes = (".mov", ".mp4")
gif_filetypes = (".gif", ".gifv")


def split_filename(file):
    split = os.path.splitext(file)
    return split[0], split[1]

def clean_string(s):
    for c in replace_chars:
        s = s.replace(c, '')
    return s

# post class
class Post:    

    def __init__(self):
        self.title = ""
        self.author = ""
        self.subreddit = ""
        
        self.folder = ""
        self.filename = ""
        self.ext = ""
        
        self.url = ""
        self.permalink = ""
        
        self.tags = []
        self.groups = []
        
        self.img_data = None
        
        self.timestamp = 0
        self.views = 0
        self.time_viewed = 0

        self.loaded = False
        self.cur_img = None
        self.frames = []
        self.frame_idx = 0

        self.temp_added_count = 0
        self.post_idx = 0

        self.times_last_post = 0

        self.blacklisted_groups = []

        self.ignore = False

    def get_idx(self):
        return self.posts_idx

    def add_time_viewed(self, time):
        self.time_viewed += time

    def viewed(self):
        self.views += 1

    def get_views(self):
        return self.views

    def set_idx(self, x):
        self.posts_idx = x

    def add_blacklisted_group(self, group):
        if group not in self.blacklisted_groups:
            self.blacklisted_groups.append(group)

    def build_from_file(self, folder, file):
        self.filename, self.ext = split_filename(file)
        self.folder = folder
        self.title = clean_string(self.filename)

    def build_from_post(self, post_data):
        self.title = post_data.title
        self.author = str(post_data.author)
        self.subreddit = post_data.subreddit.display_name
        self.url = post_data.url
        self.permalink = post_data.permalink

    def set_filename(self, folder, filename, ext):
        self.folder = folder
        self.filename = filename
        self.ext = ext

    def set_ext(ext):
        self.ext = ext
    
    def get_filename(self):
        return "{}{}{}".format(self.folder, self.filename, self.ext)

    def get_short_filename(self):
        return "{}{}".format(self.filename, self.ext)

    def is_image(self):
        return self.ext in image_filetypes

    def is_gif(self):
        return self.ext in gif_filetypes

    def is_video(self):
        return self.ext in video_filetypes

    def added_to_temp_set(self):
        self.temp_added_count += 1

    def add_media(self, m):
        self.img_data = m

    def get_all_info(self):
        info = list([
            self.title, 
            self.subreddit, 
            self.poster, 
            self.timestamp, 
            self.url,
            self.permalink, 
            self.img_data, 
            self.img_filename, 
            self.img_ext, 
            self.tags, 
            self.saved])
        self.info_list = info
        return info
    
    def file_exists(self):
        exists = True
        # print(self.get_filename())
        return exists

    def get_media(self):
        data = None
        if self.file_exists():
            if self.is_video():
                data = self.get_video()
            elif self.is_gif():
                data = self.get_gif()
            elif self.is_image():
                data = self.get_image()
        return data


    # use PIL to read data of one image
    # change max size depending on layout or monitor size?
    def get_image(self):
        """Generate image data using PIL
        """
        if not self.loaded:                     # tkinter is inactive the first time
            img = Image.open(self.get_filename())
            img.thumbnail((1250, 800))
            self.loaded = True
            self.cur_img = img
        return ImageTk.PhotoImage(self.cur_img)
    # ------------------------------------------------------------------------------

    def get_gif(self):

        if not self.loaded:
            img = Image.open(self.get_filename())
            img.thumbnail((1250, 800))
            self.loaded = True
            self.cur_img = img
            self.frame_idx = 0
            self.n_frames = img.n_frames

            # self.cur_img.seek(self.frame_idx)
            # self.cur_img.show()
        else:
            self.get_next_frame()
            self.cur_img.seek(self.frame_idx)
            # print(self.cur_img.tell())
            # print(self.cur_img.tell())
            # self.cur_img.show()
        return ImageTk.PhotoImage(self.cur_img)

    # def get_time_remaining(self):
        

    def unload_image(self):
        self.cur_img.close()
        self.loaded = False
        self.cur_img = None
        self.frames = []

    def get_next_frame(self):
        self.frame_idx = self.cur_img.tell() + 1
        if self.frame_idx >= self.n_frames:
            self.frame_idx = 0
        

    def get_video(self):
        return self.get_filename()

    def download_post_data(self):
        # post_data = requests.get(self.permalink).content
        

        print(self.url)
        print(self.permalink)
        url = ""
        if "redgifs" in self.url:
            url = "https://thumbs2.redgifs.com/" + self.url[26:] + ".mp4"
            url = ""
        elif "imgur.com" in self.url:
            url = self.url

        print(url)
        if len(url) > 1:
            with ydl:
                result = ydl.download(
                    url
                )

            data = None
            if 'entries' in result:
                # Can be a playlist or a list of videos
                data = result['entries'][0]
            else:
                # Just a video
                data = result

            video_url = data['url']
            print(video_url)
            print(data)
        else:
            print("could not get a good url for post")

    

    # getter and setters
    def add_tag(self, t):
        if not t in self.tags:
            self.tags.append(t)

    def remove_tag(self, t):
        if t in self.tags:
            self.tags.remove(t)

    def add_group(self, g):
        if not g in self.groups:
            self.groups.append(g)

    def set_title(self, t):
        self.title = t

    def get_tags(self, format='row'):
        s = ""
        if format == 'row':
            for t in self.tags:
                s += t + " "
        elif format == 'col':
            for t in self.tags:
                s += t + "\n"
        return s


    def get_filename(self):
        return "{}/{}{}".format(self.folder, self.filename, self.ext)

    def exited_post(self):
        self.times_last_post = 0


# add a variable which means a tag is required no matter what
# example: group name: Sex
#   requires sex tag, and any of [doggy, missionary, pronebone, riding]
# example: group name: Solo
#   requires toy tag, and any of [doggy, missionary, pronebone, riding]

# group class
class Group:

    def __init__(self, name, min_tags=1):
        self.name = name
        self.min_tags = 1
        self.tags = []
        self.required_tags = []

    def add_tag(self, t):
        if t not in self.tags:
            self.tags.append(t)

    def add_tags(self, ts):
        for t in ts:
            if t not in self.tags:
                self.tags.append(t)

    def add_required_tag(self, t):
        if t not in self.required_tags:
            self.required_tags.append(t)

    def add_req(self):
        self.required_tags = []

    def set_min_tags(self, t):
        self.min_tags = t

    def set_name(self, n):
        self.name = n

    def get_formatted_tags(self, format='row'):
        s = ""
        if format == 'row':
            if len(self.required_tags) > 0:
                s += "Needs: "
            for t in self.required_tags:
                s += t + ", "
            s += "\n"
            for t in self.tags:
                s += t + ", "
        elif format == 'col':
            for t in self.required_tags:
                s += "Needs:" + t + "\n"
            for t in self.tags:
                s += t + "\n"
        return s

    def get_formatted_info(self):
        s = "{} - {} free tags:".format(self.name, self.min_tags)
        for t in self.required_tags:
            s += "\n\tNeed: " + t
        for t in self.tags:
            s += "\n\t" + t
        return s




class Frame_Selector:
    
    def __init__(self, layout_shape=(1,1)):
        self.x = 1
        self.y = 1

        self.wide = layout_shape[0]
        self.high = layout_shape[1]

        self.layout_shape = layout_shape

        self.size = self.wide*self.high

    # wraps around
    def right(self):
        self.x += 1
        if self.x > self.wide:
            self.x = 1

    def left(self):
        self.x -= 1
        if self.x < 1:
            self.x = self.wide

    def up(self):
        self.y -= 1
        if self.y < 1:
            self.y = self.high

    def down(self):
        self.y += 1
        if self.y > self.high:
            self.y = 1

    def get_idx(self):
        return self.x-1 + self.y-1

    def get_key(self, item_name):
        return "_{}_{}{}_".format(item_name, self.x, self.y)

    def get_key_at(self, item_name, x, y):
        return "_{}_{}{}_".format(item_name,x, y)

