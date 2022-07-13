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
from os.path import exists

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

def post_in_database(post):
    return session.query(Post).filter_by(title=post.title, author=post.author).count() > 0

def get_matching_post(post):
    return session.query(Post).filter_by(title=post.title, author=post.author, subreddit=post.subreddit).first()

# for t in tags:
#     tag = session.query(Tag).filter_by(value=t).first()
#     if tag is None:
#         tag = Tag(t)
#         session.add(tag)
    

# for g in groups:
#     group = session.query(Group).filter_by(name=g.name).first()
#     if group is None:
#         group = Group(g.name)
#         session.add(group)
#     for t in g.tags:
#         tag = session.query(Tag).filter_by(value=t).first()
#         if tag is not None:
#             group.add_tag(tag)
#         else:
#             tag = Tag(t)
#             session.add(tag)


a = 0
for p in posts:
    post = Post(p.title, p.author, p.subreddit, p.url, p.permalink)
    post.file_saved(p.folder, p.filename, p.ext)
    if post.ext and '.' in post.ext:
        post.ext = post.ext[1:]
    if not exists(post.get_filename()):
        post.downloaded = False
        a += 1
    session.add(post)
    session.commit()

    for t in p.tags:
        tag = session.query(Tag).filter_by(value=t).first()
        if tag is not None:
            # pass
            post.add_tag(tag)
        # else:
        #     print(t)
            
temp_sets = [[],[],[],[]]
temp_sets = pickler.load(settings['tempsets_file'], temp_sets)

c1 = Collection('wife material')
c2 = Collection('girls masturbating')
c3 = Collection('quality fucking scenes')
c4 = Collection('daddys girls')

session.add(c1)
session.add(c2)
session.add(c3)
session.add(c4)
session.commit()
collections = [c1, c2, c3, c4]


# collections = session.query(Collection).all()



# for group in session.query(Group).all():
#     for tag in group.tags:
#         print(f'{group} {tag}')

for i, temp_set in enumerate(temp_sets):
    collection = collections[i]
    for p in temp_set:
        post = get_matching_post(p)
        if post is not None:
            collection.add_post(post)
            session.commit()
        else:
            print("failed to find post {p.title}")
    print(collection.posts.count())


# some cleanups for data switch
# change ext to have no . prefix
# this script for that stuff

# session.commit()
# i = 0
# j = 0
# for post in session.query(Post):



# print(i)
# print(j)
# print(a)

# session.commit()
