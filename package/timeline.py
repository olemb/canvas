import math
import cairo
from .clips import get_start_and_end

def convert_color(string):
    rgba = []
    string = string.lstrip('#')
    while string:
        char, string = string[:2], string[2:]
        rgba.append(int(char, 16) / 255)
    return tuple(rgba)

BRIGHT_COLORS = {
    'background': convert_color('ffffffff')[:3],
    'normal-clip': convert_color('b4780068'),
    'selected-clip': convert_color('0062a468'),
    'muted-clip': convert_color('c4c3c468'),
    'muted-selected-clip': convert_color('0092d438'),
    'clip-stroke': convert_color('000000ff'),
    'play-cursor': convert_color('dddddd7f'),
    'record-cursor': convert_color('ff0000ff'),
}

DARK_COLORS = {
    'background': convert_color('000000ff')[:3],
    'normal-clip': convert_color('c4880068'),
    'selected-clip': convert_color('0092d468'),
    'muted-clip': convert_color('c4c3c438'),
    'muted-selected-clip': convert_color('0092d438'),
    'clip-stroke': None,
    'play-cursor': convert_color('dddddd7f'),
    'record-cursor': convert_color('ff0000ff'),
}


COLORS = DARK_COLORS
CLIP_HEIGHT_SCALE = 0.048
MIN_DRAW_LENGTH = 60 * 1
MIN_CLIP_LENGTH = 8

class Timeline:
    def __init__(self, transport):
        self.transport = transport
        self.surface = None
        self.context = None
        self.width = None
        self.height = None
        self.xscale = None
        self.yscale = None
        self.collision_boxes = []
        self.clip_height = None

        self._make_surface(10, 10)

    def _make_surface(self, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          width, height)
        self.context = cairo.Context(self.surface)
        self.clip_height = height * CLIP_HEIGHT_SCALE

    def render(self, width, height):
        if self.surface is None:
            self._make_surface(width, height)
        elif (width, height) != (self.surface.get_width(),
                                 self.surface.get_height()):
            self.surface.finish()
            self._make_surface(width, height)

        clips = self.transport.clips
        _, end = get_start_and_end(clips)
        end = max(MIN_DRAW_LENGTH, end)
        self.width = width
        self.height = height
        self.xscale = 1 / (end) * self.width
        self.yscale = self.height

        self.draw_background()

        ctx = self.context

        ctx.save()
        self.collision_boxes = [(self.draw_clip(clip), clip) for clip in clips]
        self.collision_boxes.reverse()
        self.draw_cursor()
        ctx.restore()

        return self.surface

    def draw_background(self):
        ctx = self.context
        ctx.set_source_rgb(*COLORS['background'])
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

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
                
        ctx = self.context

        box = (clip.start * self.xscale,
               (clip.y * self.yscale) - (self.clip_height / 2),
               max(MIN_CLIP_LENGTH, clip.length * self.xscale),
               self.clip_height)
        ctx.save()

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
        pos = self.transport.pos
        y = self.transport.y

        ctx = self.context
        ctx.save()
        if self.transport.recording:
            ctx.set_source_rgba(*COLORS['record-cursor'])
        else:
            ctx.set_source_rgba(*COLORS['play-cursor'])

        # Vertical.
        x = self.transport.pos * self.xscale
        ctx.set_line_width(2)
        ctx.move_to(x, 0)
        ctx.line_to(x, self.height)
        ctx.stroke()

        # Horizontal.
        height = self.clip_height
        x = 0
        y = (y * self.height) - (self.clip_height / 2)
        ctx.set_source_rgba(0.5, 0.5, 0.5, 0.15)
        ctx.rectangle(x, y, self.width, height)
        ctx.fill()

        ctx.restore()

    def get_collision(self, x, y):
        # Todo: why is this function called tons of times every time
        # you click?
        clips = []
        for (box, clip) in self.collision_boxes:
            (cx, cy, width, height) = box
            if (cx <= x <= (cx + width)) and (cy <= y <= (cy + height)):
                clips.append(clip)
        return clips

    def set_cursor(self, x, y):
        # This is done here because the cursor must be constrained within
        # the screen, not the recording.
        # (Don't allow dragging the cursor outside the screen.)
        self.transport.pos = max(0, (min(self.width, x) / self.xscale))
        self.transport.y = max(0, min(1, y / self.yscale))

    def save_screenshot(self, filename):
        self.surface.surface.write_to_png(filename)
