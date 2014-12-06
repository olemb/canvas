import sys
from gi.repository import Gtk, Gdk, GObject
import cairo
from . import audio
from .timeline import Timeline
from .transport import Transport

class GUI(Gtk.Window):
    def __init__(self, dirname):
        super(GUI, self).__init__()
        self.transport = Transport(dirname)
        self.timeline = Timeline(self.transport)
        self.done = False

        self.dragging_clip = None
        self.clip_drag_distance = 0
        self.click_x = 0
        self.click_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.dragging_cursor = False
        self.mouse_moved = False
        self.last_cursor_pos = 0

        self.init()

    def init(self):
        self.area = Gtk.DrawingArea()
        self.area.set_size_request(600, 400)
        self.area.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.area.connect('draw', self.on_draw)
        self.connect('configure-event', self.on_resize)
        self.area.connect('button-press-event', self.on_button_press)
        self.area.connect('button-release-event', self.on_button_release)
        self.area.connect('motion-notify-event', self.on_mouse_motion)
        self.add(self.area)

        self.connect('key-press-event', self.on_key_press_event)
        self.connect('key-release-event', self.on_key_release_event)

        self.set_title('Timeline')
        # self.resize(self.width, self.height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('delete-event', self.quit)

        self.on_timer()

        self.show_all()

        sys.excepthook = self.on_exception

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
        key_name = Gdk.keyval_name(event.keyval)
        key = event.keyval

        if key == Gdk.KEY_BackSpace:
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
            if self.transport.recording:
                self.transport.stop_recording()
            else:
                self.transport.start_recording()
                self.autosave()
        elif key == Gdk.KEY_space:
            if self.transport.playing:
                self.transport.stop()
            else:
                self.transport.play()
        self.draw()

    def on_key_release_event(self, widget, event):
        key_name = Gdk.keyval_name(event.keyval)
        # print(key_name, 'released')

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.mouse_moved = False
            self.last_mouse_x = self.click_x = event.x
            self.last_mouse_y = self.click_y = event.y

            clips = self.timeline.get_collision(event.x, event.y)

            if clips:
                self.dragging_clip = clips[0]
                self.clip_drag_distance = 0
            else:
                self.transport.deselect_all()
                self.timeline.set_cursor(event.x, event.y)
                self.dragging_cursor = True
        self.draw()

    def on_mouse_motion(self, widget, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.last_mouse_x += dx
        self.last_mouse_y += dy

        if self.dragging_clip:
            clip = self.dragging_clip
            clip.y += (dy / self.timeline.yscale)
            # Don't allow dragging the clip outside the screen.
            clip.y = max(0, clip.y)
            clip.y = min(1, clip.y)
        elif self.dragging_cursor:
            self.timeline.set_cursor(self.last_mouse_x, self.last_mouse_y)
            # Todo: scrub.

        self.draw()
        self.mouse_moved = True
 
    def on_button_release(self, widget, event):
        # Deselect all clips.
        # Todo: shift?

        if self.dragging_clip:
            if not self.mouse_moved:
                clip = self.dragging_clip
                selected = clip.selected
                self.transport.deselect_all()
                clip.selected = True
            self.dragging_clip = None
            self.autosave()
        elif self.dragging_cursor:
            self.dragging_cursor = False
        self.draw()

    def on_resize(self, widget, event):
        pass

    def on_exception(self, type, value, traceback):
        if type is KeyboardInterrupt:
            self.quit()
        else:
            raise

    def autosave(self):
        self.transport.save()

    def run(self):
        try:
            Gtk.main()
        except KeyboardInterrupt:
            print('!!!')

    def quit(self, *_, **__):
        if not self.done:
            # Todo: save.
            Gtk.main_quit()
            self.transport.stop()
            self.transport.save()
            self.transport.save_mix()
            audio.terminate()
            self.done = True
