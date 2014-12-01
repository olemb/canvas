import math
import cairo

WIDTH, HEIGHT = 1600, 900
COLORS = {
    'normal-clip': (0.83, 0.6, 0.0, 0.4),
    # 'normal-stroke': (0, 0, 0, 1),
    'soloed-clip': (1.0, 0.0, 0.0, 0.4),
    'selected-clip': (0.0, 0.57, 0.83, 0.4),
    'muted-clip': (0.77, 0.77, 0.77, 0.4),
    'clip-stroke': (0, 0, 0, 1),
    'play-cursor': (0, 0, 0, 0.5),
    'record-cursor': (1, 0, 0, 1),
}
CLIP_HEIGHT = 30

class Timeline:
    def __init__(self):
        self.surface = None
        self.context = None

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
            self._make_surface()

        self.draw_background()
        self.draw_cursor(120, 0.5)

        self.draw_clip(20, 200, 0.5, 'normal')
        self.draw_clip(10, 30, 0.49, 'normal')
        self.draw_clip(20, 100, 0.6, 'selected')
        self.draw_clip(10, 200, 0.7, 'soloed')
        self.draw_clip(10, 100, 0.8, 'muted')

        return self.surface

    def draw_background(self):
        ctx = self.context
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, WIDTH, HEIGHT) # Rectangle(x0, y0, x1, y1)
        ctx.fill()

    def draw_clip(self, start, length, y, mode='normal'):
        ctx = self.context
        # Use middle of clip for position.
        y *= HEIGHT
        y -= (CLIP_HEIGHT / 2)

        # Todo: save box for collision detection.
        box = [start, y, length, CLIP_HEIGHT]
        ctx.save()
        # ctx.set_antialias(cairo.ANTIALIAS_NONE)
        ctx.set_line_width(1)

        ctx.set_source_rgba(*COLORS[mode + '-clip'])
        ctx.rectangle(*box)
        ctx.fill_preserve()
        ctx.set_source_rgba(*COLORS['clip-stroke'])
        ctx.stroke()
        ctx.restore()

    def draw_cursor(self, x, y, recording=False):
        ctx = self.context
        x *= WIDTH
        y *= HEIGHT
        ctx.save()
        if recording:
            ctx.set_source_rgba(*COLORS['record-cursor'])
        else:
            ctx.set_source_rgba(*COLORS['play-cursor'])

        # Horizontal.
        ctx.set_line_width(1)
        ctx.move_to(0, y)
        ctx.line_to(WIDTH, y)
        ctx.stroke()

        # Vertical.
        ctx.set_line_width(2)
        ctx.move_to(x, 0)
        ctx.line_to(x, HEIGHT)
        ctx.stroke()

        ctx.restore()

    def save_screenshot(self, filename):
        self.surface.surface.write_to_png(filename) # Output to PNG
