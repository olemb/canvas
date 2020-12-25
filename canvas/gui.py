import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
from .timeline import Timeline
from .transport import Transport

class GUI(Gtk.Window):
    def __init__(self, dirname):
        super(GUI, self).__init__()
        self.transport = Transport(dirname)
        self.timeline = Timeline(self.transport)
        self.done = False

        self.start_x = 0
        self.start_y = 0
        self.last_x = 0
        self.last_y = 0
        self.clips_to_drag = None
        self.dragging_clips = False
        self.dragging_cursor = False
        self.mouse_moved = False
        self.last_cursor_pos = 0

        # These two seem to do the same thing.
        # self.fullscreen()
        self.maximize()

        self.init()

    def init(self):
        self.area = Gtk.DrawingArea()
        self.area.set_size_request(600, 400)
        self.area.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.area.connect('draw', self.on_draw)
        self.area.connect('button-press-event', self.on_button_press)
        self.area.connect('button-release-event', self.on_button_release)
        self.area.connect('motion-notify-event', self.on_mouse_motion)
        self.add(self.area)

        self.connect('key-press-event', self.on_key_press_event)
        self.connect('key-release-event', self.on_key_release_event)

        self.set_title('Timeline')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('delete-event', self.close)

        self.on_timer()

        self.show_all()

    def on_timer(self):
        pos = self.transport.pos
        if pos != self.last_cursor_pos:
            self.draw()
        self.last_cursor_pos = pos
        GObject.timeout_add(100, self.on_timer)

    def draw(self):
        self.area.queue_draw()

    def on_draw(self, area, context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()
        context.set_source_surface(self.timeline.render(width, height))
        context.paint()

    def on_key_press_event(self, widget, event):
        key_name = event.string
        key = event.keyval

        if key in (Gdk.KEY_BackSpace, Gdk.KEY_Delete):
            self.transport.delete()
            self.autosave()
        elif key == Gdk.KEY_Left:
            self.transport.pos -= 1
        elif key == Gdk.KEY_Right:
            self.transport.pos += 1
        elif key == Gdk.KEY_Up:
            self.transport.y -= 0.05
        elif key == Gdk.KEY_Down:
            self.transport.y += 0.05
        elif key == Gdk.KEY_Return:
            if self.transport.toggle_recording():
                self.autosave()
        elif key == Gdk.KEY_space:
            self.transport.toggle_playback()
        elif key == Gdk.KEY_Tab:
            self.transport.select_next()
        elif key == Gdk.KEY_ISO_Left_Tab:
            self.transport.select_next(reverse=True)
        elif key_name == 's':
            self.transport.solo = True
        elif key_name == 'm':
            self.transport.mute_or_unmute_selection()
            self.autosave()

        elif key_name == 'q':
            # Record
            self.transport.stop()
            self.autosave()
            self.transport.start_recording()
        elif key_name == 'w':
            # Play back.
            self.transport.stop()
            self.autosave()
            self.transport.play()
            # Delete.
        elif key_name == 'e':
            self.transport.delete()
            self.autosave()

        self.draw()

    def on_key_release_event(self, widget, event):
        key_name = event.string
        if key_name == 's':
            self.transport.solo = False
        self.draw()

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.mouse_moved = False
            self.last_x = self.start_x = event.x
            self.last_y = self.start_y = event.y

            clips = self.timeline.get_collision(event.x, event.y)

            if clips:
                # Just drag the first clip.
                # (Todo: drag selected clips?)
                self.clips_to_drag = clips[:1]
            else:
                self.transport.deselect_all()
                self.timeline.set_cursor(event.x, event.y)
                self.dragging_cursor = True
        self.draw()

    def on_mouse_motion(self, widget, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.last_x += dx
        self.last_y += dy

        if self.clips_to_drag:
            if self.dragging_clips:
                for clip in self.clips_to_drag:
                    clip.y += (dy / self.timeline.yscale)
                    # Don't allow dragging the clip outside the screen.
                    clip.y = max(0, clip.y)
                    clip.y = min(1, clip.y)
            else:
                # If we've moved more than 5 pixels from
                # where we clicked, start dragging the clip.
                dx2 = abs(event.x - self.start_x)
                dy2 = abs(event.y - self.start_y)
                if dx2 > 5 or dy2 > 5:
                    self.start_x = event.x
                    self.start_y = event.y
                    self.dragging_clips = True
        elif self.dragging_cursor:
            self.timeline.set_cursor(self.last_x, self.last_y)
            # Todo: scrub.

        self.draw()
        self.mouse_moved = True

    def on_button_release(self, widget, event):
        # Deselect all clips.
        # Todo: shift?
        shift_held = bool(int(event.state) & 1)

        if event.button == 1:
            if self.dragging_clips:
                self.autosave()
            else:
                if self.clips_to_drag:
                    # Deselect other clips unless shift is
                    # held down. (1 == shift.)
                    # Todo: this should use SHIFT_MASK but
                    # there's no obvious way to do that.
                    clip = self.clips_to_drag[0]

                    if shift_held:
                        clip.selected = not clip.selected
                    else:
                        self.transport.deselect_all()
                        self.clips_to_drag[0].selected = True

            self.clips_to_drag = None
            self.dragging_clips = False
            self.dragging_cursor = False

        self.draw()

    def autosave(self):
        self.transport.save()

    def run(self):
        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.close()

    def close(self, *_, **__):
        if not self.done:
            Gtk.main_quit()
            self.transport.stop()
            self.transport.save()
            self.transport.save_mix()
            self.transport.close()
            self.done = True
            super(GUI, self).close()
