### Immediate todo
	


#### Temp Sets
	reorder posts in temp set, moving it left or right


#### Media Controls
	Pause / Play
	Skip Ahead / Back (with repeated presses ex: [5, 10, 15, 30])
	Volume Up / Down



create set on the fly
	press key to add or remove a post to a set of posts
	the set of posts can be reset anytime but is empty on startup
make set of posts as a class
	so you can most easily manipulate sets of posts
	adding or removing pots, shuffling, storing
update tag ui on remove tag
make tag viewing work
make way to remove tag and group and group tag from editor
scripts for merging data
	tags, groups, posts
when adding tags from subreddit 
	if the start of the subreddit is "u_" ignore it 
	at end go over list of tags
		go from smallest to biggest words
		if word is inside another word add those to a set called the smallest word
		after show those "duplicates" to the user so they can say if they are different tags or not
			ex/ dadwouldbeproud, daddy -> dad set with those two tags in it
			a "word" is 2 to 8 characters? cant be too large would take forever


reddit viewier
==============
log in to reddit and get posts from a certain category
	all subs
	group
	single sub
	users posts
sort the posts
	hot
	recent
	top within time frame
when viewing post you can save it, upvote, download it

advanced filters
	range of upvotes
	upvotes vs current top post on that sub overall or users subed
	


reddit browser for porn
=======================
allows you to browse reddit (anon if you prefer to not save in reddit?)
save posts but to a database
	this database can be enormous and not delete old posts (unlike reddit wtf)
when you view you saved posts its now displayed so much better
	grid or list view
	pictures only, titles
	upvotes/downvotes disabled, view of them, can sort if you want for some reason, but also search range
you can tag posts
search is so much better, looks at titles, tags, ml guess, date posted range, upvote range, comments, subreddits in
you can make groups or themes
modes:
	view - saved, new (hot/top week/rising etc),  
	poster (redditor) - sorting modes, inbox and chat, stats

Some tag suggest modes
	low use tags
		uses low use tags, if they are not used often
		or tags taht are almost always coupled with other tags
	high use tags
		highest use tags will suggest more often


reddit saved post downloader
=============================
when you download it shouldnt overwrite the files that already exist
should still attempt to download all photos
unless I can figure out a way to tell it how many to download
	stop trying to add posts when we reach a title that already exists
	

groups
========================
you can make a group with tag, also can be recomended tags
	recomended ones based off of machine learning vs your current saved posts (wow a use no way)
posts belong to a group if they have the right vars (if statement)
	from behind: tags=[ass, frogbutt, below, behind, spread, solo, amateur], subreddits=[frogbutt, spread_em]
		tags and subreddit default bool logic is any
		can say has to have X amount of correct features to be allowed tho
		could also have ones that are higher priority for finer control, solo=2, normaly each worth 1 here solo worth 2
you can add or remove items from a group but by default if they are part of a group they are a part of it
can be part of multiple groups
group intersection, suggests areas where groups mix
can use these groups to suggest a multireddit to browse from (default the sum of the subreddits that pics belong to)
when you are in a group you can go into different views

views
=========================
views are in the main_view screen
views are like layouts for pictures and info
can have pics in certain way or certain groups in a view
views by default move to next every 10 seconds, staggered too?
you can click or press space to advance to next
stop slide shows with tab
shift or right click for context menu to change view settings
w a s d work for keys too can change view targetting, left handed controls
couple modes for groups
saved only, hot, top week/year/all, 

if you find a redditor who posts good stuff you can do a couple things
follow them, count total posts and on startup see if they posted new stuff
if so you parse their posts and currate a list of these posts
parsing a redditors posts is getting all the posts theyve made, filtering out irrelevant subreddits
then getting the posts theyve made and comparing them for differences
can be done either by getting all posts made ~10 mins apart for a certain range
then comparing those vs eachother or picking highest 5 since thats probably close enough
when following you can also auto save posts if the fall under criteria



what do i need to do to make it
================================
download all saved posts for a user
setup tags
optional, sort posts, can do as you please
view setup
	shuffle, select layout, next pic speed, auto advance, tagging mode, 
display picture slideshow

look at the posts and depending on the site scrape it differently
	redgifs -> add .mp4 to that url and download it
	imgur -> add ext to it and download it

look for ways to download anyfile type from a url

make a gui that is a frame that displays images or video
make the gui goto next item in list

string stuff
=============
something to clean strings
but also categorize words that show up often as keyboards
maybe to format urls?
capitalize strings for url, its 3 letters out of ~30?
could get mobile version but make clear?
something to resize files too
portrait sizes and crop the file to it temporarily
 
Merge folder data with reddit data
=============
could compare the image data
if the image data matches
	combine the tags from the fold into reddit ones
	



slideshow
=================
can rate and tag pictures that are on being displayed
when the pictures displayed you can input 3 different tags that are displayed
if you dont input it doesnt mean it isnt that tag but wont suggest for a bit
you can ctrl (key) to do an anti-tag, this is more for ml butwont suggest again



#### Post Dating / Ordering
	Reddit gives newest posts first and we dont know how many posts we will scrape
	we get all the posts then flip the order and label each
	get index of old saved posts
	go +1 and set that as index for all new posts
	append that to the old posts (old posts are already labeled)
	then your posts will be saved from 1 to xxx where 1 is the oldest post we could scrape

	allow for sorting by date in groups
	