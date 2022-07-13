from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base, session
from datetime import datetime
from time import time

from PIL import Image, ImageTk

image_filetypes = ('jpeg', 'jpg', 'png')
video_filetypes = ('mp4', 'mov', 'gifv')
gif_filetypes = ('gif')

post_tags = Table('post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

def get_all_model_entries(model):
    entries = session.query(model).all()
    return entries


class Post(Base):
    __tablename__ = 'post'
    # __tableargs__ = {'extend_exisiting' : True}
    id = Column(Integer, primary_key=True, unique=True)

    title = Column(String(140), index=True)
    subreddit = Column(String(140), index=True)
    
    author = Column(String(140), index=True)
    
    filename = Column(String(140))
    folder = Column(String(10))
    ext = Column(String(6))

    timestamp = Column(DateTime, index=True, default=datetime.utcnow)

    # url points to the media location
    url = Column(String(140))
    # permalink points to the reddit link
    permalink = Column(String(140))

    views = Column(Integer)
    times_last_viewed = Column(Integer)
    # total time viewing the post
    time_viewed = Column(Integer)

    ignore = Column(Boolean)

    is_image = Column(Boolean)
    is_video = Column(Boolean)
    is_gif = Column(Boolean)

    downloaded = Column(Boolean)
    sitename = Column(String(100))

    file_deleted = Column(Boolean)
    failed_downloads = Column(Integer)




    tags = relationship('Tag', secondary=post_tags, backref='post', lazy='dynamic')

    # column for if image / video / gif ?

    def __init__(self, title, author, subreddit, url, permalink):
        self.title             = title
        self.author            = author
        self.subreddit         = subreddit
        self.url               = url
        self.permalink         = permalink
        self.views             = 0
        self.times_last_viewed = 0
        self.time_viewed       = 0
        self.ignore            = False

        self.is_image = False
        self.is_video = False
        self.is_gif = False
        self.downloaded = False
        self.sitename = ''
        self.file_deleted = False
        self.failed_downloads = 0


    def __repr__(self):
        return '<Post {}>'.format(self.title)

    def get_tags_flattened(self):
        return [tag.value for tag in self.tags]

    def get_tags_formatted_stacked(self):
        tags = self.get_tags_flattened()
        s = ''
        for t in tags:
            s += t + '\n'
        return s

    def add_tag(self, tag):
        if not self.has_tag(tag):
            self.tags.append(tag)

    def remove_tag(self, tag):
        if self.has_tag(tag):
            self.tags.remove(tag)
    
    def has_tag(self, tag):
        return self.tags.filter_by(id=tag.id).count() > 0

    def is_image(self):
        return self.ext in image_filetypes
        
    def is_video(self):
        return self.ext in video_filetypes
        
    def is_gif(self):
        return self.ext in gif_filetypes

    def failed_download(self):
        self.failed_downloads += 1

    def file_saved(self, folder, filename, ext):
        self.folder = folder
        self.filename = filename
        self.ext = ext

        self.is_image = self.ext in image_filetypes
        self.is_video = self.ext in video_filetypes
        self.is_gif = self.ext in gif_filetypes

        self.downloaded = True

    def file_deleted(self):
        self.downloaded = False

    def get_filename(self):
        return f'{self.folder}/{self.filename}.{self.ext}'

    def get_short_filename(self):
        return f'{self.filename}.{self.ext}'

    def viewed(self):
        self.views += 1
        
    def exited_post(self):
        self.times_last_viewed += 1
        
    def get_media(self):
        data = None
        if self.downloaded:
            if self.is_video():
                data = self.get_video()
            elif self.is_gif():
                data = self.get_gif()
            elif self.is_image():
                data = self.get_image()
        return data
        
    def get_image(self):
        img = Image.open(self.get_filename())
        img.thumbnail((1250, 800))
        return ImageTk.PhotoImage(img)
    # ------------------------------------------------------------------------------

    def get_gif(self):
        return ''

    def unload_image(self):
        # self.cur_img.close()
        # self.loaded = False
        # self.cur_img = None
        # self.frames = []
        pass

    def get_next_frame(self):
        self.frame_idx = self.cur_img.tell() + 1
        if self.frame_idx >= self.n_frames:
            self.frame_idx = 0

    def get_video(self):
        return self.get_filename()


class Tag(Base):
    __tablename__ = 'tag' 
    id = Column(Integer, primary_key=True, unique=True)
    
    value = Column(String(70), index=True)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Tag {}>'.format(self.value)
        
class Group(Base):
    __tablename__ = 'group' 
    id = Column(Integer, primary_key=True, unique=True)
    
    name = Column(String(70), index=True)
    
    tags = relationship('Tag', secondary='group_tag', viewonly=True, lazy='dynamic') 

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Group {}: {}>'.format(self.name, self.get_tags_flattened())

    def add_tag(self, tag):
        if not self.contains(tag):
            self.tags.append(GroupTag(group=self, tag=tag))

    def remove_tag(self, tag):
        if self.contains(tag):
            gt = session.query(GroupTag).filter_by(group_id=self.id, tag_id=tag.id).first()
            session.delete(gt)

    def get_tags_flattened(self):
        return [tag.value for tag in self.tags] 
    
    def contains(self, tag):
        return self.tags.filter_by(id=tag.id).count() > 0

        
class GroupTag(Base):
    __tablename__ = 'group_tag' 
    id = Column(Integer, primary_key=True, unique=True)
    
    group_id = Column(Integer, ForeignKey('group.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    group = relationship('Group', backref=backref('group_tag', cascade='all, delete-orphan'))
    tag = relationship('Tag', backref=backref('group_tag', cascade='all, delete-orphan'))

    def __init__(self, group, tag):
        self.group = group
        self.tag = tag

    def __repr__(self):
        return '<GroupTag {} - {}>'.format(self.group.name, self.tag.value)

class Collection(Base):
    __tablename__ = 'collection'
    id = Column(Integer, primary_key=True, unique=True)

    name = Column(String(140), index=True)

    posts = relationship('Post', secondary='collection_post', viewonly=True, lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Collection {}>'.format(self.name)
        
    def add_post(self, post):
        if not self.contains(post):
            self.posts.append(CollectionPost(collection=self, post=post))

    def remove_post(self, post):
        if self.contains(post):
            self.posts.remove(post)

    def contains(self, post):
        return self.posts.filter_by(id=post.id).count() > 0

class CollectionPost(Base):
    __tablename__ = 'collection_post'
    id = Column(Integer, primary_key=True, unique=True)

    collection_id = Column(Integer, ForeignKey('collection.id'))
    post_id = Column(Integer, ForeignKey('post.id'))

    collection = relationship('Collection', backref=backref('collection_post', cascade='all, delete-orphan'))
    post = relationship('Post', backref=backref('collection_post', cascade='all, delete-orphan'))

    def __init__(self, collection, post):
        self.collection = collection
        self.post = post

    def __repr__(self):
        return '<CollectionPost {} - {}>'.format(self.collection.name, self.post.title)

        