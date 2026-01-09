# https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html
# https://doc.qt.io/qtforpython-6/examples/example_quick_scenegraph_openglunderqml.html#example-quick-scenegraph-openglunderqml
from PySide6 import QtWidgets, QtGui, Qt, QtCore
from .timeline import Timeline  # noqa: E402
from .transport import Transport  # noqa: E402

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, transport):
        super().__init__()
        
        self.setMouseTracking(True)

        self.transport = transport
        self.timeline = Timeline(transport)
        self.done = False

        self.label = QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap(800, 600)
        self.label.setPixmap(self.pixmap)
        self.setCentralWidget(self.label)

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
        # self.maximize()

        ## self.area.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
        # self.area.connect('draw', self.on_draw)

        self.draw()

    def draw(self):
        pixmap = self.label.pixmap()
        self.timeline.render(pixmap)
        self.label.setPixmap(pixmap)
        self.timer = QtCore.QTimer()
        self.timer.singleShot(100, self.draw)

    def request_draw(self):
        ##pos = self.transport.pos
        ##if pos != self.last_cursor_pos:
        self.draw()
        
    def on_timer(self):
        self.last_cursor_pos = pos
        # GObject.timeout_add(100, self.on_timer)        

    # def draw(self):
    #     self.area.queue_draw()

    def on_draw(self, area, context):
        raise NotImplemented()

        width = area.get_allocated_width()
        height = area.get_allocated_height()
        context.set_source_surface(self.timeline.render(width, height))
        context.paint()

    def keyPressEvent(self, event):
        print(self.transport.pos)
    
        key_name = event.text()
        key = event.key()
        qt = QtCore.Qt

        if key in (qt.Key_Backspace, qt.Key_Delete):
            self.transport.delete()
            self.autosave()
        elif key == qt.Key_Left:
            self.transport.pos -= 1
        elif key == qt.Key_Right:
            self.transport.pos += 1
        elif key == qt.Key_Up:
            self.transport.y -= 0.05
        elif key == qt.Key_Down:
            self.transport.y += 0.05
        elif key == qt.Key_Return:
            if self.transport.toggle_recording():
                self.autosave()
        elif key == qt.Key_Space:
            self.transport.toggle_playback()
        elif key == qt.Key_Tab:
            self.transport.select_next()
        # elif key == Gdk.KEY_ISO_Left_Tab:
        #     self.transport.select_next(reverse=True)
        elif event.text == 's':
            self.transport.solo = True
        elif event.text == 'm':
            self.transport.mute_or_unmute_selection()
            self.autosave()

        self.request_draw()

    def keyReleaseEvent(self, event):
        if event.text == 's':
            self.transport.solo = False
        self.request_draw()

    def mousePressEvent(self, event):
        # TODO: why is this not found?
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_moved = False
            self.last_x = self.start_x = event.x
            self.last_y = self.start_y = event.y

            clips = self.timeline.get_collision(event.x, event.y)

            if clips:
                if clips[0].selected:
                    self.clips_to_drag = self.transport.get_selected_clips()
                else:
                    # Just drag the first clip.
                    self.clips_to_drag = clips[:1]
            else:
                self.transport.deselect_all()
                self.timeline.set_cursor(event.x, event.y)
                self.dragging_cursor = True
        self.request_draw()

    def mouseMoveEvent(self, event):
        print(event.x)
        raise NotImplemented()

        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.last_x += dx
        self.last_y += dy

        if self.clips_to_drag:
            if self.dragging_clips:
                for clip in self.clips_to_drag:
                    clip.y += dy / self.timeline.yscale
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

        self.draw()
        self.mouse_moved = True

    def mouseReleaseEvent(self, event):
        # TODO: implement:
        ## shift_held = bool(int(event.state) & 1)
        shift_held = False

        if event.button == 1:
            if self.dragging_clips:
                self.autosave()
            else:
                if self.clips_to_drag:
                    # Deselect other clips unless shift is
                    # held down.
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
        self.app.exec_()

    def close(self, *_, **__):
        if not self.done:
            self.app.quit()
            print(self.transport.pos)
            self.transport.stop()
            self.transport.save()
            self.transport.save_mix()
            self.transport.close()
            self.done = True


def run(transport):
    # TODO: handle sys.argv here?
    app = QtWidgets.QApplication([])
    window = MainWindow(transport)
    window.show()
    app.exec()
