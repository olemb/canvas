# https://www.pythonguis.com/tutorials/pyside6-bitmap-graphics/
from PySide6 import QtGui
from .clips import get_start_and_end

def convert_color(string):
    rgba = []
    string = string.lstrip('#')
    while string:
        char, string = string[:2], string[2:]
        rgba.append(int(char, 16) / 255)
    return tuple(rgba)


COLORS = {
    'background': convert_color('000000'),
    'normal-clip': convert_color('c4880068'),
    'selected-clip': convert_color('0092d468'),
    'muted-clip': convert_color('c4c3c438'),
    'muted-selected-clip': convert_color('0092d438'),
    'clip-stroke': None,
    'play-cursor': convert_color('dddddd7f'),
    'record-cursor': convert_color('ff0000ff'),
}


CLIP_HEIGHT_SCALE = 0.048
MIN_DRAW_LENGTH = 60 * 1
MIN_CLIP_LENGTH = 8



class Timeline:
    def __init__(self, transport):
        self.transport = transport
        self.width = None
        self.height = None
        self.xscale = None
        self.yscale = None
        self.clip_height = None
        self.collision_boxes = []

    def render(self, pixmap):
        self.pixmap = pixmap
        self.painter = QtGui.QPainter(pixmap)
        self.pen = QtGui.QPen()
        self.painter.setPen(self.pen)

        self.width = pixmap.width()
        self.height = pixmap.height()
        self.clip_height = pixmap.height() * CLIP_HEIGHT_SCALE        

        clips = self.transport.clips
        _, end = get_start_and_end(clips)
        end = max(MIN_DRAW_LENGTH, end)
        # Subtract 5 so the recording cursor will not be off-screen.
        self.xscale = 1 / (end) * (self.width - 5)
        self.yscale = self.height

        self.pixmap.fill(QtGui.QColor('white'))

        #self.collision_boxes = [(self.draw_clip(clip), clip) for clip in clips]
        #self.collision_boxes.reverse()
        self.draw_cursor()

        del self.painter
        self.painter = None

    def draw_clip(self, clip):
        if self.transport.solo:
            if clip.selected:
                color = COLORS['selected-clip']
            else:
                color = COLORS['muted-clip']
        else:
            if clip.selected and clip.muted:
                color = COLORS['muted-selected-clip']
            elif clip.selected:
                color = COLORS['selected-clip']
            elif clip.muted:
                color = COLORS['muted-clip']
            else:
                color = COLORS['normal-clip']

            box = (
                clip.start * self.xscale,
                (clip.y * self.yscale) - (self.clip_height / 2),
                max(MIN_CLIP_LENGTH, clip.length * self.xscale),
                self.clip_height,
            )

            ctx.set_source_rgba(*color)
            stroke_color = COLORS['clip-stroke']
            if stroke_color:
                ctx.rectangle(*box)
                ctx.fill_preserve()
                ctx.set_source_rgba(*stroke_color)
                ctx.set_line_width(1)
                ctx.stroke()
            else:
                ctx.rectangle(*box)
                ctx.fill()

            ctx.restore()

            return box

    def draw_cursor(self):
        y = self.transport.y

        if self.transport.recording:
            self.pen.setColor(QtGui.QColor(*COLORS['record-cursor']))
        else:
            self.pen.setColor(QtGui.QColor(*COLORS['play-cursor']))

        # Vertical cursor (pos).
        x = self.transport.pos * self.xscale
        self.pen.setWidth(5)
        self.painter.drawLine(x, 0, x, self.height)

        return

        # Horizontal cursor (y).
        height = self.clip_height
        x = 0
        y = (y * self.height) - (self.clip_height / 2)
        ctx.set_source_rgba(0.5, 0.5, 0.5, 0.15)
        ctx.rectangle(x, y, self.width, height)
        ctx.fill()

    def get_collision(self, x, y):
        clips = []
        for (box, clip) in self.collision_boxes:
            (cx, cy, width, height) = box
            if (cx <= x <= (cx + width)) and (cy <= y <= (cy + height)):
                clips.append(clip)
        return clips

    def set_cursor(self, x, y):
        # This is done here because the cursor must be constrained within
        # the timeline display, not the recording.
        # (Don't allow dragging the cursor outside the screen.)
        self.transport.pos = max(0, (min(self.width, x) / self.xscale))
        self.transport.y = max(0, min(1, y / self.yscale))

    def save_screenshot(self, filename):
        self.surface.surface.write_to_png(filename)
