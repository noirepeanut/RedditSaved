from database import session
import random
from sqlalchemy.sql.expression import func, select

from models import Post, Tag, Group, Collection, CollectionPost

# views for the database, set of posts 
# also functions for sorting


def next_id(query, id):
	if id == query.count()-1:
		id = 0
	else:
		id += 1
	return id

def prev_id(query, id):
	if id == 0:
		id = query.count()-1
	else:
		id -= 1
	return id

# sorting

def sort_new(query):
	return query.order_by(None).order_by(Post.timestamp.desc())

def sort_old(query):
	return query.order_by(None).order_by(Post.timestamp.asc())

def shuffle(query):
	return query.order_by(func.random())

def all_posts():
	return session.query(Post)

def any_tagged():
	return session.query(Post).filter(Post.tags.any())

def not_tagged():
	return session.query(Post).filter(Post.tags.count() == 0)

def min_n_tags(n):
	return session.query(Post).filter(Post.tags.count() == n)

def search_group(name):
	return session.query(Group).filter_by(name=name)

def search_collection(name):
	return session.query(Collection).filter_by(name=name)

def search_group(name):
	return session.query(Group).filter_by(name=name)

def search_tag(value):
	return session.query(Tag).filter_by(value=value)

def collection(id):
	return session.query(Collection).filter_by(id=id).first().posts

def group(g):
	return session.query(Group).filter_by(id=g.id).first().posts

def tag(id):
	return session.query(Tag).filter_by(id=id).first().posts

def with_tag(tag):
	return session.query(Post).filter(Post.has_tag(tag))

def select_random(query):
	return random.choice(query.all())

def images_only(query):
	return query.filter(Post.is_image())

def videos_only(query):
	return query.filter(Post.is_video())

def gifs_only(query):
	return query.filter(Post.is_gif())