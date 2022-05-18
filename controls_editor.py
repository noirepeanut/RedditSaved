import PySimpleGUI as sg


import pickler

##### controls for this program
quit_program = [sg.WIN_CLOSED, 'Exit']



# location of tag and group data
controls_file = "data/controls.dat"

######### Functions
def format_controls_table(controls):
    table = []
    i = 0
    for key in controls:
        values = ""
        for c in controls[key]:
            if c == " ":
                c = "\'SPACE\'"
            elif c == None:
                c = "None"
            values += c + "  "
        row = [key, values]
        # row = [key, controls[key]]
        table.append(row)
        i += 1
    return table

def clean_event(event):
    if type(event) == type("") and ":" in event:
        parts = event.split(":")
        event = parts[0]
    return event


def main():
    # if this filename changes we need to update for each file
    settings_file = 'data/settings.dat'
    settings = pickler.load(settings_file)

    controls = pickler.load(settings['controls_file'])

    sg.theme(settings['theme'])

    ######## GUI SETUP
    controls_elem = sg.Table(headings=["Action", "Controls / Events"], 
        values=format_controls_table(controls), key="_CONTROLS_TABLE_", 
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        num_rows=None, expand_x=True, expand_y=True,
        font='20',
        enable_click_events=True)

    default_input_status_text = "Select Action to Modify its Controls"
    inputting_control_elem = sg.Text(default_input_status_text, key="_INPUT_STATUS_")

    clear_controls_elem = sg.Button("Clear Controls", key="_CLEAR_CONTROLS_")



    layout = [[inputting_control_elem], [clear_controls_elem], [controls_elem]]



    # setup the window
    window = sg.Window("Controls Editor", layout, return_keyboard_events=True, auto_size_text=True, use_default_focus=True, size=(1100, 700))


    inputting_control = False
    input_control_key = None



    ####### program loop
    while True:
        
        event, values = window.read(timeout=None)

        event = clean_event(event)
        # print("Event: {}  |  Values: {}".format(event, values))


        if event in (sg.WIN_CLOSED, 'Exit'):
            if inputting_control:
                inputting_control = False
            else:
                break

        elif "_CONTROLS_TABLE_" in event:
            row = event[2][0]
            row_selected = window["_CONTROLS_TABLE_"].get()[row]
            input_control_key = row_selected[0]
            # print(controls[input_control_key])
            inputting_control = True

        elif "_CLEAR_CONTROLS_" in event and input_control_key != None:
            controls[input_control_key] = []
            window['_CONTROLS_TABLE_'].update(format_controls_table(controls))
            input_control_key = None
            inputting_control = False
        
        elif inputting_control:
            controls[input_control_key].append(event)
            window['_CONTROLS_TABLE_'].update(format_controls_table(controls))
            input_control_key = None
            inputting_control = False
        
        if inputting_control:
            window["_INPUT_STATUS_"].update("Press key to add as control for {} action".format(input_control_key))
        else:
            window["_INPUT_STATUS_"].update(default_input_status_text)

    window.close()

    # before we quit save the data
    pickler.save(controls, controls_file)
