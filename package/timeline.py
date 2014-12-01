import math
import cairo
from .clips import get_start_and_end

COLORS = {
    'normal-clip': (0.83, 0.6, 0.0, 0.4),
    # 'normal-stroke': (0, 0, 0, 1),
    'soloed-clip': (1.0, 0.0, 0.0, 0.4),
    'selected-clip': (0.0, 0.57, 0.83, 0.8),
    'muted-clip': (0.77, 0.77, 0.77, 0.3),
    'clip-stroke': (0, 0, 0, 1),
    'play-cursor': (0, 0, 0, 0.5),
    'record-cursor': (1, 0, 0, 1),
}
CLIP_HEIGHT = 30
MIN_DRAW_LENGTH = 60 * 1

class Timeline:
    def __init__(self, clips):
        self.clips = clips
        self.surface = None
        self.context = None
        self.width = None
        self.height = None
        self.xscale = None
        self.yscale = None
        self.collision_boxes = []

    def _make_surface(self, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          width, height)
        self.context = cairo.Context(self.surface)
        

    def render(self, width, height):
        if self.surface is None:
            self._make_surface(width, height)
        elif (width, height) != (self.surface.get_width(),
                                 self.surface.get_height()):
            self.surface.finish()
            self._make_surface(width, height)

        _, end = get_start_and_end(self.clips)
        end = max(MIN_DRAW_LENGTH, end)
        self.width = width
        self.height = height
        self.xscale = 1 / (end) * self.width
        self.yscale = self.height

        self.draw_background()

        ctx = self.context

        ctx.save()
        for clip in self.clips:
            box = self.draw_clip(clip)
            self.collision_boxes.append((box, clip))
        self.collision_boxes.reverse()

        self.draw_cursor(pos=10, y=0.5, recording=False)
        ctx.restore()

        return self.surface

    def draw_background(self):
        ctx = self.context
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

    def draw_clip(self, clip):
        if clip.selected:
            color = COLORS['selected-clip']
        elif clip.muted:
            color = COLORS['muted-clip']
        else:
            color = COLORS['normal-clip']

        ctx = self.context

        # Todo: save box for collision detection.
        box = (clip.start * self.xscale,
               (clip.y * self.yscale) - (CLIP_HEIGHT / 2),
               max(16, clip.length * self.xscale),
               CLIP_HEIGHT)
        ctx.save()
        # ctx.set_antialias(cairo.ANTIALIAS_NONE)
        ctx.set_line_width(1)

        ctx.set_source_rgba(*color)
        ctx.rectangle(*box)
        ctx.fill_preserve()
        ctx.set_source_rgba(*COLORS['clip-stroke'])
        ctx.stroke()
        ctx.restore()

        return box

    def draw_cursor(self, pos, y, recording=False):
        ctx = self.context
        x = pos * self.xscale
        y = y * self.height
        ctx.save()
        if recording:
            ctx.set_source_rgba(*COLORS['record-cursor'])
        else:
            ctx.set_source_rgba(*COLORS['play-cursor'])

        # Horizontal.
        ctx.set_line_width(1)
        ctx.move_to(0, y)
        ctx.line_to(self.width, y)
        ctx.stroke()

        # Vertical.
        ctx.set_line_width(2)
        ctx.move_to(x, 0)
        ctx.line_to(x, self.height)
        ctx.stroke()

        ctx.restore()

    def save_screenshot(self, filename):
        self.surface.surface.write_to_png(filename)

