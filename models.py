from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base
from datetime import datetime
from time import time


image_filetypes = ('.jpeg', '.jpg', '.png')
video_filetypes = ('.mp4', '.mov', '.gifv')
gif_filetypes = ('.gif')

class Post(Base):
    __tablename__ = 'post' 
    id = Column(Integer, primary_key=True, unique=True)

    title = Column(String(140), index=True)
    subreddit = Column(String(140), index=True)
    
    author = Column(String(140), index=True)
    
    filename = Column(String(140))
    folder = Column(String(10))
    ext = Column(String(6))

    timestamp = Column(Date, index=True, default=datetime.utcnow)

    # url points to the media location
    url = Column(String(140))
    # permalink points to the reddit link
    permalink = Column(String(140))

    views = Column(Integer, default=0)
    times_last_viewed = Column(Integer, default=0)
    # total time viewing the post
    time_viewed = Column(Integer, default=0)

    ignore = Column(Boolean, default=False)

    # column for if image / video / gif ?

    def __init__(self, title, author, subreddit, url, permalink, filename, folder, ext):
        self.title     = title
        self.author    = author
        self.subreddit = subreddit
        self.url       = url
        self.permalink = permalink
        self.filename  = filename
        self.folder    = folder
        self.ext       = ext

    def __repr__(self):
        return '<Post {}>'.format(self.title)

class Tag(Base):
    __tablename__ = 'tag' 
    id = Column(Integer, primary_key=True, unique=True)
    
    value = Column(String(70), index=True)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Tag {}>'.format(self.value)
        
class PostTag(Base):
    __tablename__ = 'post_tag' 
    id = Column(Integer, primary_key=True, unique=True)
    
    post_id = Column(Integer, ForeignKey('post.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)

    post = relationship('Post', backref=backref('PostTag', cascade='all, delete-orphan'))
    tag = relationship('Tag', backref=backref('PostTag', cascade='all, delete-orphan'))

    def __repr__(self):
        return '<PostTag {} - {}>'.format(self.post.title, self.tag.value)
