import sys
import webbrowser
import os



from agilette.modules.library import Library

lib = Library('/Users/jonathan/0_jono_data')

out_path = 'df.html'

lib.metadata_table.to_html(out_path)

webbrowser.open('file:///' + os.getcwd() + '/' + out_path)