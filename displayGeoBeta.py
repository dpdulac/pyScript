"""
NAME: displayGeoBeta
ICON: icon.png
KEYBOARD_SHORTCUT: Ctrl+Shift+Z
SCOPE:
display geometry without opening the sceneGraph

"""

# The following symbols are added when run as a shelf item script:
# exit():      Allows 'error-free' early exit from the script.
# console_print(message, raiseTab=False):
#              Prints the given message to the result area of the largest
#              available Python tab.
#              If raiseTab is passed as True, the tab will be raised to the
#              front in its pane.
#              If no Python tab exists, prints the message to the shell.
# console_clear(raiseTab=False):
#              Clears the result area of the largest available Python tab.
#              If raiseTab is passed as True, the tab will be raised to the
#              front in its pane.
import sys
import displayGeoScript as disp

if sys.version_info[0] == 3:
    import importlib
    importlib.reload(disp)
    print("python 3")
else:
    reload(disp)
    print("python 2")
disp.BuildisplayGeoUI()



