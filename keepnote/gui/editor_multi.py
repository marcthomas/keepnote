"""

    KeepNote
    MultiEditor widget in main window

    This editor contain multiple editors that can be switched based on
    the content-type of the node.

"""


#
#  KeepNote
#  Copyright (c) 2008-2009 Matt Rasmussen
#  Author: Matt Rasmussen <rasmus@mit.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#


# pygtk imports
import pygtk
pygtk.require('2.0')
from gtk import gdk
import gtk.glade
import gobject

# keepnote imports
import keepnote
from keepnote.gui.editor import KeepNoteEditor

_ = keepnote.translate


class MultiEditor (KeepNoteEditor):
    """
    Manager for switching between multiple editors
    """

    def __init__(self, app):
        KeepNoteEditor.__init__(self, app)
        self.show_all()

        self._notebook = None
        self._pages = []
        self._editor = None
        self._window = None
        self._use_minitoolbar = False


    def set_editor(self, editor):

        # do nothing if editor is already set
        if editor == self._editor:
            return

        # tear down old editor, if it exists
        if self._editor:
            self._editor.view_pages([])
            self._editor.save_preferences(self._app.pref)
            if self._window:
                self._editor.remove_ui(self._window)
            self._editor.set_notebook(None)
            self.remove(self._editor)

        self._editor = editor

        # start up new editor, if it exists
        if self._editor:
            self.pack_start(self._editor, True, True, 0)
            self._editor.show()
            self._editor.set_notebook(self._notebook)
            if self._window:
                self._editor.add_ui(self._window, self._use_minitoolbar)
            self._editor.load_preferences(self._app.pref)
            self._editor.view_pages(self._pages)


    #========================================
    # Editor Interface

    def set_notebook(self, notebook):
        """Set notebook for editor"""
        self._notebook = notebook
        if self._editor:
            self._editor.set_notebook(notebook)
        
    def is_focus(self):
        """Return True if text editor has focus"""
        if self._editor:
            return self._editor.is_focus()
        return False

    def grab_focus(self):
        """Pass focus to textview"""
        if self._editor:
            return self._editor.grab_focus()

    def clear_view(self):
        """Clear editor view"""
        if self._editor:
            return self._editor.clear_view()
    
    def view_pages(self, pages):
        """View a page in the editor"""
        self._pages = pages[:]
        if self._editor:
            return self._editor.view_pages(pages)
    
    def save(self):
        """Save the loaded page"""
        if self._editor:
            return self._editor.save()

        
    def save_needed(self):
        """Returns True if textview is modified"""
        if self._editor:
            return self._editor.save_needed()
        return False

    def load_preferences(self, app_pref, first_open=False):
        """Load application preferences"""
        if self._editor:
            return self._editor.load_preferences(app_pref, first_open)
        

    def save_preferences(self, app_pref):
        """Save application preferences"""
        if self._editor:
            return self._editor.save_preferences(app_pref)
        

    def add_ui(self, window, use_minitoolbar=False):
        self._window = window
        self._use_minitoolbar = use_minitoolbar
        if self._editor:
            return self._editor.add_ui(window, use_minitoolbar)


    def remove_ui(self, window):
        self._window = None
        if self._editor:
            return self._editor.remove_ui(window)
                         
    def undo(self):
        if self._editor:
            return self._editor.undo()

    def redo(self):
        if self._editor:
            return self._editor.redo()


class ContentEditor (MultiEditor):
    """
    Register multiple editors depending on the content type
    """

    def __init__(self, app):
        MultiEditor.__init__(self, app)
        
        self._editors = {}
        self._default_editor = None


    def add_editor(self, content_type, editor):
        self._editors[content_type] = editor

    def removed_editor(self, content_type):
        del self._editors[content_type]

    def get_editor(self, content_type):
        return self._editors[content_type]

    def set_default_editor(self, editor):
        self._default_editor = editor

    #=============================
    # Editor Interface

    def view_pages(self, pages):

        if len(pages) != 1:
            MultiEditor.view_pages(self, [])
        else:
            content_type = pages[0].get_attr("content_type").split("/")

            for i in xrange(len(content_type), 0, -1):
                editor = self._editors.get("/".join(content_type[:i]), None)
                if editor:
                    self.set_editor(editor)
                    break
            else:
                self.set_editor(self._default_editor)

            MultiEditor.view_pages(self, pages)

