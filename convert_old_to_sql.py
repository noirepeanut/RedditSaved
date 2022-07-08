# read tags and group files
# for each tag and group
#   create a new tag or group entry
#
# read the posts.dat file
# for each post
#   make a new post
#   copy its tags
#
# for the sets create a new set

from models import Post, Tag, Group, GroupTag, Collection, CollectionPost
from database import session
import pickler


settings_file = 'data/settings.dat'
settings = pickler.load(settings_file)

saved_post_dir = settings['media_dir']
data_dir = settings['data_dir']

posts_data_file = settings['posts_data_file']
tags_file = settings['tags_file']
groups_file = settings['groups_file']


# load data
tags = pickler.load(tags_file)
groups = pickler.load(groups_file)
posts = pickler.load(posts_data_file)

for t in tags:
    tag = Tag(t)
    session.add(tag)
    
session.commit()

for g in groups:
    group = Group(g.name)
    session.add(group)
    for t in g.tags:
        tag = session.query(Tag).filter_by(value=t).first()
        group.add_tag(tag)
        
session.commit()

for p in posts:
    post = Post(p.title, p.author, p.subreddit, p.url, p.permalink, p.filename, p.folder, p.ext)
    for t in post.tags:
        tag = session.query(Tag).filter_by(value=t).first()
        post.add_tag(tag)

session.commit()

