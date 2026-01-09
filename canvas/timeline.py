# https://www.pythonguis.com/tutorials/pyside6-bitmap-graphics/
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



def render_timeline(pixmap, transport):
    width = None
    height = None
    xscale = None
    yscale = None
    clip_height = None
    collision_boxes = []
    
    width = pixmap.width()
    height = pixmap.height()
    clip_height = height * CLIP_HEIGHT_SCALE

    # TODO: use COLORS['background'] instead.
    pixmap.fill('black')    
    
    return

    clips = self.transport.clips
    _, end = get_start_and_end(clips)
    end = max(MIN_DRAW_LENGTH, end)
    # Subtract 5 so the recording cursor will not be off-screen.
    self.xscale = 1 / (end) * (self.width - 5)
    self.yscale = self.height

    ctx = self.context
    
    ctx.save()
    self.collision_boxes = [(self.draw_clip(clip), clip) for clip in clips]
    self.collision_boxes.reverse()
    self.draw_cursor()
    ctx.restore()
    
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
            ctx.save()

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

        painter = QtGui.Painter(self.pixmap)
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
