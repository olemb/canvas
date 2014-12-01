#!/usr/bin/env python3
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

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# ctx.scale(WIDTH, HEIGHT) # Normalizing the canvas

ctx.set_source_rgb(1, 1, 1)
ctx.rectangle(0, 0, WIDTH, HEIGHT) # Rectangle(x0, y0, x1, y1)
ctx.fill()

def draw_clip(start, length, y, mode='normal'):
    # Use middle of clip for position.
    y *= HEIGHT
    y -= (CLIP_HEIGHT / 2)

    # Todo: save box for collision detection.
    box = [start, y, length, CLIP_HEIGHT]
    print(box)
    ctx.save()
    # ctx.set_antialias(cairo.ANTIALIAS_NONE)
    ctx.set_line_width(1)

    ctx.set_source_rgba(*COLORS[mode + '-clip'])
    ctx.rectangle(*box)
    ctx.fill_preserve()
    ctx.set_source_rgba(*COLORS['clip-stroke'])
    ctx.stroke()
    ctx.restore()

def draw_cursor(x, y, recording=False):
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
    
draw_clip(20, 300, 0.5, 'normal')
draw_clip(10, 30, 0.49, 'normal')
draw_clip(20, 100, 0.6, 'selected')
draw_clip(10, 200, 0.7, 'soloed')
draw_clip(10, 100, 0.8, 'muted')

draw_cursor(0.5, 0.5)
# draw_cursor(0.7, 0.9, recording=True)

surface.write_to_png("example.png") # Output to PNG
