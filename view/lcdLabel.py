#!/usr/bin/python
# -*- coding: latin1 -*-

# Copyright (C) 2005 Gerome Fournier <jefke(at)free.fr>
# Copyright (C) 2008 Frédéric Mantegazza <fma@gbiloba.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Problems:
#     * don't display text given before parent window is shown

import sys
import os.path

import gtk
import gtk.glade

CHARS_FILENAME = "lcdLabelChars.txt"


class LCDLabel(gtk.DrawingArea):
    """ GTK LCD Widget
    """
    def __init__(self, text=None):
        """ Init LCD widget
        """
        gtk.DrawingArea.__init__(self)
        self._text = text
        
        self._table = {}
        self._pixmap = None

        self._width_chars = 10
        self._border = 5
        self._cborder = 3
        self._cwidth = 9
        self._cheight = 13
        self._width = 2 * self._border + (self._cwidth + self._cborder) * self._width_chars + self._cborder
        self._height = 2 * self._border + (self._cheight + self._cborder) * 1 + self._cborder
        self.set_size_request(self._width, self._height)

        self.connect("configure_event", self._configure)
        self.connect("expose_event", self._expose)

    def _configure(self, widget, event):
        print "_configure()"
        if self._pixmap is None:
            x, y, width, height = widget.get_allocation()
            self._pixmap = gtk.gdk.Pixmap(widget.window, width, height)
            self.set_brightness(100)
            self._pixmap.draw_rectangle(self._back, True, 0, 0, width, height)
        #self._load_font_definition() # Already done in set_brightness()
        #self.clear()
        return True
        
    def _expose(self, widget, event):
        print "_expose()"
        if self._pixmap is not None:
            widget.window.draw_drawable(self._back, self._pixmap, 0, 0, 0, 0, self._width, self._height)
        return False

    def set_width_chars(self, n_chars):
        """ Set the desired width in chars of the LCD widget
        """
        print "set_width_chars()"
        self._width_chars = n_chars
        self._width = 2 * self._border + (self._cwidth + self._cborder) * self._width_chars + self._cborder
        self.refresh()

    def get_width_chars(self):
        """ Return the width (in chars) of the widget
        """
        return self._width_chars

    def refresh(self):
        """ Refresh the LCD widget
        """
        print "refresh()"
        self.queue_draw_area(0, 0, self._width, self._height)

    def set_text(self, text):
        """ Set the LCD label text
        """
        print "set_text()"
        self._text = text
        if self._pixmap is not None:
            self.clear()
            for col, char in enumerate(text):
                self._draw_char(col, ord(char))
            #self.refresh() # Not needed

    def get_text(self):
        """ Return the LCD label text
        """
        return self._text

    def _draw_char(self, col, char_index):
        """ Draw the character stored at position 'char_index' in the internal
        character definition table, on the LCD widget
        """
        if self._pixmap is not None:
            x = col * (self._cwidth + self._cborder) + self._border + self._cborder
            y = 0 + self._border + self._cborder
            self._pixmap.draw_drawable(self._back, self._table[char_index], 0, 0, x, y, self._cwidth, self._cheight)

    def set_brightness(self, brightness):
        print "set_brightness()"
        fg_colors = {
            100: "#00ff96",
            75: "#00d980",
            50: "#00b269",
            25: "#008c53",
            0: "#303030"
        }
        if brightness not in fg_colors.keys():
            return
        if hasattr(self, "_brightness") and self._brightness == brightness:
            return
        self._brightness = brightness
        self._set_colors(["#000000", "#303030", fg_colors[brightness]])
        self._load_font_definition()
        
    def get_brightness(self):
        return self._brightness

    def clear(self):
        print "clear()"
        """ Clear the LCD display
        """
        for col in range(self._width_chars):
            self._draw_char(col, 32)
        self.refresh()

    def create_char(self, charindex, shape):
        """Insert a new char in the character table definition,
           at position 'charindex', based on 'shape'
        """
        pixmap = gtk.gdk.Pixmap(self.window, self._cwidth, self._cheight)
        pixmap.draw_rectangle(self._back, True, 0, 0, self._cwidth, self._cheight)
        for x in range(5):
            for y in range(7):
                pixmap.draw_rectangle(self._charbg, True, x * 2, y * 2 , 1, 1)
        for index in range(35):
            if shape[index] == "1":
                row = index / 5
                col = index - row * 5
                pixmap.draw_rectangle(self._charfg, True, col * 2, row * 2, 1, 1)
        self._table[charindex] = pixmap

    def _set_colors(self, colors):
        print "set_colors()"
        for widget, color in zip(["_back", "_charbg", "_charfg"], colors):
            exec "self.%s = gtk.gdk.GC(self._pixmap)" % widget
            exec "self.%s.set_rgb_fg_color(gtk.gdk.color_parse('%s'))" % (widget, color)

    def _load_font_definition(self):
        """ Load character table definition from file
        """
        print "_load_font_definition()"
        file = open(os.path.join(os.path.dirname(__file__), CHARS_FILENAME))
        index = 1
        shape = ""
        for line in file.readlines():
            line = line.rstrip()
            if not line or line[0] == '#':
                continue
            if index == 1:
                iChar = int(line, 16)
            else:
                shape = "".join([shape, line])
            index += 1
            if index == 9:
                self.create_char(iChar, shape)
                index = 1
                shape = ""


def main():
    def on_button_clicked(self):
        lcdLabel.set_text("PIPO") # Text given here is corectly displayed
        lcdLabel.set_width_chars(6)
        
    window = gtk.Window()
    vbox = gtk.VBox()
    window.add(vbox)
    lcdLabel = LCDLabel("TEST") # Text given here is not displayed
    vbox.add(lcdLabel)
    button = gtk.Button("Click")
    button.connect("clicked", on_button_clicked)
    vbox.add(button)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    #lcdLabel.set_text("TEST") # Text given here is corectly displayed
    gtk.main()


if __name__ == "__main__":
    main()