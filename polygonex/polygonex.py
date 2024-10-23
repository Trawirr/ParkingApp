import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import time

class Polygonex:
    def __init__(self) -> None:
        self._image_name = None
        self._image = None
        self._polygons_json = None
        self._points = []
        self._zoom = 1
        self._point_tmp = None
        self._fig = self._ax = None

    def load_image(self, image_path: str) -> None:
        # loading image
        self._image = mpimg.imread(image_path)
        image_name = image_path
        for sep in ['\\']:
            image_name = image_name.replace(sep, '/')
        image_name = ''.join(image_name.split('/')[-1].split('.')[:-1])
        self._image_name = image_name
        print(f"{self._image.shape=}")

        # loading json
        json_path = ''.join(image_path.split('.')[:-1]) + '.json'
        # DOKONCZYC
        

    def display_image(self):
        self._fig, self._ax = plt.subplots()
        self._ax.imshow(self._image)

        self._click_cid = self._fig.canvas.mpl_connect('button_press_event', self.on_click)
        self._scroll_cid = self._fig.canvas.mpl_connect('scroll_event', self.on_scroll)

        print(f"{self._ax.get_ylim()}")
        plt.show()

    def on_scroll(self, event):
        print("scroll", event.step, event.xdata, event.ydata)
        self._zoom = max(1, self._zoom + event.step)
        self._center = [event.xdata, event.ydata]
        self.update_image()

    def on_click(self, event):
        x, y = event.xdata, event.ydata
        print("clicked", event.button, x, y)
        if x is not None and y is not None:
            # LMB - add point to polygon
            if event.button == 1:
                if self._points:
                    self._ax.plot([self._points[-1][0], x], [self._points[-1][1], y], 'r-')
                    if self._point_tmp:
                        self._point_tmp[0].remove()
                        self._point_tmp = None
                else:
                    self._point_tmp = self._ax.plot(x, y, 'ro')
                self._points.append([x, y])

            # RMB - end of sequence
            elif event.button == 3:
                pass

        self.update_image()

    def update_image(self):
        print(f"updating: {self._center=}, {self._zoom=}")
        # use zoom
        height_img, width_img, _ = self._image.shape
        height_zoomed = height_img // self._zoom // 2
        width_zoomed = width_img // self._zoom // 2
        print(f"{height_img=}, {width_img=}, {self._zoom=} => {height_zoomed=}, {width_zoomed=}")

        print(f"before {self._center=}")
        # fix x
        self._center[0] += min(0, width_zoomed - self._center[0])
        self._center[0] -= min(0, self._center[0] + width_zoomed - width_img)

        # fix y
        self._center[1] += min(0, height_zoomed - self._center[1])
        self._center[1] -= min(0, self._center[1] + height_zoomed - height_img)
        print(f"after {self._center=}")

        # set lims
        self._ax.set_xlim(self._center[0] - width_zoomed, self._center[0] + width_zoomed)
        self._ax.set_ylim(self._center[1] + height_zoomed, self._center[1] - height_zoomed)        

        # draw updated image
        self._fig.canvas.draw()

# Load and display the image
def display_image(image_path):
    img = mpimg.imread(image_path)
    
    # Create a figure and axis to display the image
    fig, ax = plt.subplots()
    ax.imshow(img)
    print(ax.get_xlim(), ax.get_ylim())
    
    # Create an empty list to store the picked points
    points = []
    point_tmp = None

    # Define the function that will be called when points are picked
    def onclick(event):
        # Only accept left mouse button clicks
        if event.button == 1:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:  # Check if within the image area
                print(f"Point selected at: x={x}, y={y}")
                # Mark the point on the image
                if len(points):
                    ax.plot([points[-1][0], x], [points[-1][1], y], 'r-')  # red dot for clicked point
                    print(type(point_tmp), point_tmp)
                    point_tmp[0].remove()
                else:
                    point_tmp = ax.plot(x, y, 'ro')
                    print(type(point_tmp), point_tmp)
                points.append((x, y))
                fig.canvas.draw()

    def on_scroll(event):
        x1, x2 = ax.get_xlim()
        y1, y2 = ax.get_ylim()
        print(x1, x2, y1, y2, event.button, event.step, event.xdata, event.ydata)
        x_mid = (x1 + x2) // 2
        y_mid = (y1 + y2) // 2
        ax.set_xlim((x1 + x_mid) // 2, (x_mid + x2) // 2)
        ax.set_ylim((y1 + y_mid) // 2, (y_mid + y2) // 2)
        print("Scroll")
        ax.update(props={})
        fig.canvas.draw()

    # Connect the mouse click event to the function
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    scroll_cid = fig.canvas.mpl_connect('scroll_event', on_scroll)

    # Display the image
    plt.show()

    return points

poly = Polygonex()
poly.load_image("parking.jpg")
poly.display_image()

# # Path to your image file
# image_path = 'parking.jpg'

# # Call the function and get selected points
# selected_points = display_image(image_path)
# print("Selected points:", selected_points)
