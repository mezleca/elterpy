import json
import os
import time
import threading

import win32api, win32con
import dearpygui.dearpygui as gui

app = {
    "initialized": False,
    "stop": False,
    "thread": None
}

buttons = {
    "LEFT_BUTTON": "0x01",
    "RIGHT_BUTTON": "0x02",
    "MIDDLE_BUTTON": "0x04",
    "XBUTTON1": "0x05",
    "XBUTTON2": "0x06"
}

target_buttons = {
    "mouse1": win32con.MOUSEEVENTF_LEFTDOWN,
    "mouse2": win32con.MOUSEEVENTF_RIGHTDOWN
}

config = {
    "key": buttons.get("XBUTTON2"), # default key
    "cps": 12,
    "random": False,
    "target": "mouse1" # default target button
}

def update_config():
    with open("config.json", "w") as file:
        file.write(json.dumps(config))
        print("config update")

def create_config():
    with open("config.json", "a") as file:
        file.write(json.dumps(config))
        print("config created")

def load_config():
    with open("config.json", "r") as file:
        text = file.read()
        config.update(json.loads(text))
        print("config loaded")

if (os.access("./config.json", os.R_OK)):
    load_config()
else:
    create_config()

hotkeys = list(buttons.keys())
target_keys = list(target_buttons.keys())

def get_key_from_stupid_map(key):
    keys = list(buttons.values())
    key_index = keys.index(key)
    return list(buttons.keys())[key_index]

def hotkey_callback():
    key_code = buttons.get(gui.get_value("keys"))
    key = get_key_from_stupid_map(key_code)

    # set key
    config["key"] = key_code
                                           
    gui.set_value("current_key", f"current key: {key}")

def cps_callback():
    value = gui.get_value("cps")
    config["cps"] = value

def target_key_callback():
    target = gui.get_value("target_key")
    config["target"] = target
    gui.set_value("current_target", f"current target: {target}")

def click():
    target_event = target_buttons[config["target"]]
    win32api.mouse_event(target_event, 0, 0)
    if config["target"] == "mouse1":
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    elif config["target"] == "mouse2":
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

def yep():
    global app
    app["stop"] = True
    if app["thread"] is not None:
        app["thread"].join()
    print("finished")

def initialize():
    global app
    if app["initialized"]:
        app["stop"] = True
        app["initialized"] = False
        print("auto click disabled")
        gui.set_item_label("init", "initialize")
        return

    app["initialized"] = True
    app["stop"] = False
    gui.set_item_label("init", "stop")

    def auto_click_loop():
        while not app["stop"]:
            if win32api.GetAsyncKeyState(int(config.get("key"), 16)):
                click()
                time.sleep(1 / int(config.get("cps")))

    app["thread"] = threading.Thread(target=auto_click_loop)
    app["thread"].start()

gui.create_context()
gui.create_viewport(title="elterpy", width=600, height=400, min_width=600, max_height=400, resizable=False)
gui.setup_dearpygui()
gui.set_exit_callback(yep)

with gui.font_registry():
    main_font = gui.add_font(file="./fonts/jb.ttf", size=16)

with gui.window(label="elterpy", max_size=(600, 400), min_size=(600, 400), no_resize=True, no_title_bar=True, no_move=True):
    
    with gui.tab_bar():

        gui.bind_font(main_font)

        # options tab
        with gui.tab(label="main"):
            gui.add_button(label="initialize", callback=initialize, tag="init")
            gui.add_slider_int(label="clicks per second", callback=cps_callback, min_value=6, max_value=50, tag="cps")

        # hotkeys tab
        with gui.tab(label="hotkey"):
            gui.add_listbox(hotkeys, label="hotkeys", callback=hotkey_callback, tag="keys", tracked=True, num_items=len(hotkeys) * 2)
            current_key = get_key_from_stupid_map(config.get("key"))
            gui.add_text(f"current key: { current_key }", tag="current_key")

        # target key tab
        with gui.tab(label="target key"):
            gui.add_listbox(target_keys, label="target key", callback=target_key_callback, tag="target_key", tracked=True, num_items=len(target_keys))
            gui.add_text(f"current target: {config.get('target')}", tag="current_target")

        # config tab
        with gui.tab(label="config"):
            gui.add_button(label="save config", callback=update_config)
            gui.add_button(label="load config", callback=load_config)

with gui.theme() as theme:
    with gui.theme_component(gui.mvAll):

        gui.add_theme_color(gui.mvThemeCol_WindowBg, (16, 16, 16))
        
        gui.add_theme_style(gui.mvStyleVar_FramePadding, 4, 6)
        gui.add_theme_style(gui.mvStyleVar_TabRounding, 0.65)
        gui.add_theme_style(gui.mvStyleVar_WindowBorderSize, 0, 0)
        gui.add_theme_style(gui.mvStyleVar_Alpha, 0.85)
        gui.add_theme_style(gui.mvStyleVar_FrameRounding, 1)
    
gui.bind_theme(theme=theme)
        
gui.show_viewport()
gui.start_dearpygui()
gui.destroy_context()