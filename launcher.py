


import media_browser
import reddit_scrapper
import tag_group_editor
import controls_editor
import setup
import PySimpleGUI as sg
import pickler

settings_file = 'data/settings.dat'

def main():
	settings = pickler.load(settings_file)
	if settings == []:
		setup.main()
		settings = pickler.load(settings_file)

	sg.theme(settings['theme'])

	layout = [
		[sg.Button("Media Browser", key='_MEDIA_BROWSER_', expand_x=True)],
		[sg.Button("Scrape Reddit Posts", key='_SCRAPE_REDDIT_', expand_x=True)],
		[sg.Button("Tag and Group Editor", key='_TAG_GROUP_EDITOR_', expand_x=True)],
		[sg.Button("Change Controls", key='_CHANGE_CONTROLS_', expand_x=True)],
		[sg.Button("Edit Settings", key='_EDIT_SETTINGS_', expand_x=True)],
		[sg.Button("Quit", key='_QUIT_', expand_x=True)],
	]

	# layout = [[sg.Column(layout)]]

	window = sg.Window("Porn Organizer Launcher", layout, auto_size_buttons=True)

	launch_program = None
	while True:

		events, values = window.read(timeout=None)
 

		# if events == '_MEDIA_BROWSER_':
		# 	launch_program = 'media_browser'
		# 	break
		# elif events == '_SCRAPE_REDDIT_':
		# 	launch_program = 'scrape_reddit'
		# 	break
		# elif events == '_TAG_GROUP_EDITOR_':
		# 	launch_program = 'tag_group_editor'
		# 	break
		# elif events == '_CHANGE_CONTROLS_':
		# 	launch_program = 'change_controls'
		# 	break
		# elif events == '_EDIT_SETTINGS_':
		# 	launch_program = 'edit_settings'
		# 	break
		# elif events in ('_QUIT_', sg.WIN_CLOSED):
		# 	break


		if events == '_MEDIA_BROWSER_':
			launch_program = 'media_browser'
			break
		elif events == '_SCRAPE_REDDIT_':
			reddit_scrapper.main()
		elif events == '_TAG_GROUP_EDITOR_':
			tag_group_editor.main()
		elif events == '_CHANGE_CONTROLS_':
			controls_editor.main()
		elif events == '_EDIT_SETTINGS_':
			setup.main()
		elif events in ('_QUIT_', sg.WIN_CLOSED):
			break

	window.close()
	return launch_program

if __name__ == '__main__':
	launch_program = main()
	if launch_program == "media_browser":
		media_browser.main()
	elif launch_program == "scrape_reddit":
		reddit_scrapper.main()
	elif launch_program == "tag_group_editor":
		tag_group_editor.main()
	elif launch_program == "change_controls":
		controls_editor.main()
	elif launch_program == "edit_settings":
		setup.main()