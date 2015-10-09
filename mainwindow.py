__author__ = 'wybe'


from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import time
import copy

from pencil import Line, Pencil


class MainWindow(Gtk.Window):

    def __init__(self):
        super(MainWindow, self).__init__()

        # -- Variables --
        self._h_mirror = True
        self._v_mirror = True

        self._last_x = 0
        self._last_y = 0

        self._last_buffer_time = time.time()
        self._last_update_time = time.time()

        self._mouse_pressed = False

        self._buffer_image = None
        self._lines = []

        # ---- Initialize the pencils. ----
        self._pencils = []

        for i in range(0, 50):
            self._pencils.append(Pencil(0, 0, 0.2, 0.8, 0.8, 0.5))

        # -- Drawing area --

        self._area = Gtk.DrawingArea()

        # Capture button presses in drawing area.
        self._area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self._area.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self._area.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        # Connect events.
        self._area.connect('draw', self._draw)
        self.connect('key-press-event', self._key_press)
        self._area.connect('button-press-event', self._button_press)
        self._area.connect('button-release-event', self._button_release)
        self._area.connect('motion-notify-event', self._motion_notify)

        # Visuals update
        GLib.timeout_add(10, self._update)

        self.set_size_request(1000, 500)

        self.add(self._area)

    def _update(self):
        """
        Updates the pencils.
        """
        # Calculate delta time.
        now = time.time()
        dt = now - self._last_update_time
        self._last_update_time = now

        # Update the pencils and when the mouse is down, add the lines to the buffer.
        for pencil in self._pencils:
            line = pencil.update(dt, self._last_x, self._last_y, self._mouse_pressed)

            if line:
                self._lines.append(line)

                # ---- Mirroring. ----
                # TODO: Make better.

                if self._h_mirror:
                    mir_line = copy.copy(line)

                    width = self.get_allocated_width()
                    half_width = width / 2

                    s_x = mir_line.start_x
                    e_x = mir_line.end_x

                    if s_x > half_width:
                        s_x -= 2 * (s_x - half_width)
                    else:
                        s_x += 2 * (half_width - s_x)

                    if e_x > half_width:
                        e_x -= 2 * (e_x - half_width)
                    else:
                        e_x += 2 * (half_width - e_x)

                    mir_line.start_x = s_x
                    mir_line.end_x = e_x

                    self._lines.append(mir_line)

                    if self._v_mirror:
                        mir_line = copy.copy(mir_line)

                        height = self.get_allocated_height()
                        half_height = height / 2

                        s_y = mir_line.start_y
                        e_y = mir_line.end_y

                        if s_y > half_height:
                            s_y -= 2 * (s_y - half_height)
                        else:
                            s_y += 2 * (half_height - s_y)

                        if e_y > half_height:
                            e_y -= 2 * (e_y - half_height)
                        else:
                            e_y += 2 * (half_height - e_y)

                        mir_line.start_y = s_y
                        mir_line.end_y = e_y

                        self._lines.append(mir_line)

                if self._v_mirror:
                    mir_line = copy.copy(line)

                    height = self.get_allocated_height()
                    half_height = height / 2

                    s_y = mir_line.start_y
                    e_y = mir_line.end_y

                    if s_y > half_height:
                        s_y -= 2 * (s_y - half_height)
                    else:
                        s_y += 2 * (half_height - s_y)

                    if e_y > half_height:
                        e_y -= 2 * (e_y - half_height)
                    else:
                        e_y += 2 * (half_height - e_y)

                    mir_line.start_y = s_y
                    mir_line.end_y = e_y

                    self._lines.append(mir_line)

        self._area.queue_draw()
        return True

    def _draw(self, widget, cr):
        width = self.get_allocated_width()
        height = self.get_allocated_height()

        cr.set_operator(cairo.OPERATOR_SOURCE)

        # Background
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()

        # ---- Image ----
        if self._buffer_image:
            Gdk.cairo_set_source_pixbuf(cr, self._buffer_image, 0, 0)
            cr.paint()

        cr.set_operator(cairo.OPERATOR_ADD)

        # ---- Line buffer ----
        cr.set_line_width(1)
        for line in self._lines:
            cr.set_source_rgba(line.r, line.g, line.b, line.a)
            cr.move_to(line.start_x, line.start_y)
            cr.line_to(line.end_x, line.end_y)
            cr.stroke()

        # ---- Save the screen ----
        now = time.time()
        if now - self._last_buffer_time > 0.2:

            # Save screen.
            drawing_window = self._area.get_window()
            self._buffer_image = Gdk.pixbuf_get_from_window(drawing_window, 0, 0, width, height)

            # Clear the line buffer.
            self._lines.clear()

            # Update
            self._last_buffer_time = now

        # Circle
        cr.set_source_rgba(1, 1, 1)

        cr.arc(self._last_x, self._last_y, 25, 0, 2*math.pi)
        cr.stroke()

    def _key_press(self, widget, event):
        if event.keyval == Gdk.KEY_1:
            # Magenta color.
            for pencil in self._pencils:
                pencil._col = [0.2, 0.8, 0.8, 0.5]

        elif event.keyval == Gdk.KEY_2:
            # Red color.
            for pencil in self._pencils:
                pencil._col = [0.8, 0.2, 0.2, 0.5]

        elif event.keyval == Gdk.KEY_3:
            # Green color.
            for pencil in self._pencils:
                pencil._col = [0.2, 0.8, 0.2, 0.5]

        elif event.keyval == Gdk.KEY_4:
            # Orange color.
            for pencil in self._pencils:
                pencil._col = [0.8, 0.5, 0.2, 0.5]

        elif event.keyval == Gdk.KEY_5:
            # "Black" color.
            for pencil in self._pencils:
                pencil._col = [0.3, 0.3, 0.3, 0.5]

        elif event.keyval == Gdk.KEY_q:
            # Toggle horizontal mirror.
            self._h_mirror = not self._h_mirror

        elif event.keyval == Gdk.KEY_w:
            # Toggle vertical mirror.
            self._v_mirror = not self._v_mirror

        elif event.keyval == Gdk.KEY_z:
            # Clear screen.
            self._buffer_image = None

        elif event.keyval == Gdk.KEY_s:
            # Save screen to file.
            self._buffer_image.savev('Image.png', 'png', [], [])

    def _button_press(self, widget, event):
        if event.button == 1:
            self._mouse_pressed = True

    def _button_release(self, widget, event):
        if event.button == 1:
            self._mouse_pressed = False

    def _motion_notify(self, widget, event):
        x = event.x
        y = event.y

        self._last_x = x
        self._last_y = y
