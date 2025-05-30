import cv2
import matplotlib.pyplot as plt
import numpy as np

class PixelMeasurementTool:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image_orig = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
        self.image = self.image_orig.copy()
        self.fig, self.ax = plt.subplots()
        self.ax.imshow(self.image)
        self.points = []
        self.undo_stack = []
        self.redo_stack = []
        self.line_objects = []
        self.text_objects = []

        self.scale = 1.0
        self.offset = [0, 0]

        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.cid_scroll = self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)

        plt.title("Left Click = Point | u = Undo | r = Redo | Scroll = Zoom | q = Quit")
        plt.show()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        # Adjust click coords to image coords considering zoom and pan
        x = (event.xdata - self.offset[0]) / self.scale
        y = (event.ydata - self.offset[1]) / self.scale
        x, y = int(x), int(y)

        self.points.append((x, y))
        self.undo_stack.append(('add', (x, y)))
        self.redo_stack.clear()  # clear redo after new action

        self.redraw()

    def on_key(self, event):
        if event.key == 'u':  # Undo
            if self.undo_stack:
                self.redo_stack.append(self.undo_stack.pop())
                self.points.pop()
                self.redraw()

        elif event.key == 'r':  # Redo
            if self.redo_stack:
                action, point = self.redo_stack.pop()
                self.points.append(point)
                self.undo_stack.append((action, point))
                self.redraw()

        elif event.key == 'q':  # Quit
            plt.close(self.fig)

    def on_scroll(self, event):
        base_scale = 1.2
        old_scale = self.scale

        if event.button == 'up':
            self.scale *= base_scale
        elif event.button == 'down':
            self.scale /= base_scale
        else:
            return

        self.scale = max(0.1, min(self.scale, 10))

        xdata = event.xdata
        ydata = event.ydata

        # Adjust offset to zoom centered on mouse position
        self.offset[0] = xdata - (xdata - self.offset[0]) * (self.scale / old_scale)
        self.offset[1] = ydata - (ydata - self.offset[1]) * (self.scale / old_scale)

        self.redraw()

    def redraw(self):
        self.ax.clear()

        # Show zoomed and panned image
        self.ax.imshow(self.image_orig, extent=[self.offset[0],
                                                self.offset[0] + self.image_orig.shape[1]*self.scale,
                                                self.offset[1] + self.image_orig.shape[0]*self.scale,
                                                self.offset[1]],
                       aspect='auto')

        for i, pt in enumerate(self.points):
            x = pt[0]*self.scale + self.offset[0]
            y = pt[1]*self.scale + self.offset[1]
            self.ax.plot(x, y, 'go')
            if i >= 1:
                pt1 = self.points[i-1]
                pt2 = pt
                x1, y1 = pt1[0]*self.scale + self.offset[0], pt1[1]*self.scale + self.offset[1]
                x2, y2 = pt2[0]*self.scale + self.offset[0], pt2[1]*self.scale + self.offset[1]
                self.ax.plot([x1, x2], [y1, y2], 'r-')
                dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
                self.ax.text((x1+x2)/2, (y1+y2)/2, f'{dist:.1f}px', color='yellow', fontsize=9)

        self.ax.set_xlim(self.offset[0], self.offset[0] + self.image_orig.shape[1]*self.scale)
        self.ax.set_ylim(self.offset[1] + self.image_orig.shape[0]*self.scale, self.offset[1])
        self.ax.axis('off')
        self.fig.canvas.draw()


if __name__ == '__main__':
    image_path = r"D:\ai\subhi\1.png"  # Your image path here
    PixelMeasurementTool(image_path)
