# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html

import xbmcgui

# Text alighnment constants. Mixed variants are obtained by bit OR (|)
ALIGN_LEFT = 0
ALIGN_RIGHT = 1
ALIGN_CENTER_X = 2
ALIGN_CENTER_Y = 4
ALIGN_CENTER = 6
ALIGN_TRUNCATED = 8
ALIGN_JUSTIFY = 10

# XBMC key action codes.
# More codes at https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4


class AddonWindow:

    """
    A mini-framework for an addon control window in XBMC.

    The control windows serves as a parent widget for other XBMC UI controls
    much like Tkinter.Tk class.
    This is an abstract class which is not supposed to be instantiated directly
    and will raise NotImplementedError exeption.
    It is designed to be fully implemented in a grand-child class with the second inheritance
    from xbmcgui.Window or xbmcgui.WindowDialog in a direct child class.
    """

    def __init__(self, title=''):
        """Constructor method."""
        self.setImages()
        self.title_bar = xbmcgui.ControlLabel(-10, -10, 1, 1, title, alignment=ALIGN_CENTER)

    def setImages(self):
        """
        Set paths to images.

        The code below is the minimal example for implementation in a grand-child class.
        setImages method must have at least 2 image paths - self.background_img and self.title_background_img -
        and all geometry adjustment constants fully defined in a grand-child class.
        """
        # Window background image
        self.background_img = 'ContentPanel.png'
        # Background for the window header
        self.title_background_img = 'dialogheader.png'
        # Horisontal adjustment for a header background if the main background has transparent edges.
        self.X_MARGIN = 5
        # Vertical adjustment for a header background if the main background has transparent edges
        self.Y_MARGIN = 5
        # Header position adjustment if the main backround has visible borders.
        self.Y_SHIFT = 4
        # The height of a window header (for the title background and the title label).
        self.HEADER_HEIGHT = 35
        raise NotImplementedError('setImages method must be fully implemented in a child class!')

    def setGeometry(self, width_, height_, pos_x=0, pos_y=0):
        """
        Create a new window with given width and height, and set a backgroudnd and a title bar.
        x_, y_ - coordinates of the top level corner of the window.
        if x_=0, y_=0, the window will be placed at the center of the screen.
        """
        self.width = width_
        self.height = height_
        if pos_x and pos_y:
            self.x = pos_x
            self.y = pos_y
        else:
            self.x = 640 - self.width/2
            self.y = 360 - self.height/2
        self.background = xbmcgui.ControlImage(self.x, self.y, self.width, self.height, self.background_img)
        self.addControl(self.background)
        try:
            self.title_background = xbmcgui.ControlImage(self.x + self.X_MARGIN, self.y + self.Y_MARGIN + self.Y_SHIFT,
                                        self.width - 2 * self.X_MARGIN, self.HEADER_HEIGHT, self.title_background_img)
            self.addControl(self.title_background)
            self.title_bar.setPosition(self.x + self.X_MARGIN, self.y + self.Y_MARGIN + self.Y_SHIFT)
            self.title_bar.setWidth(self.width - 2 * self.X_MARGIN)
            self.title_bar.setHeight(self.HEADER_HEIGHT)
            self.addControl(self.title_bar)
        except NameError:
            raise NotImplementedError('setImages method must be fully implemented in a child class!')

    def setGrid(self, rows_, columns_, padding=10):
        """Set window grid layout of rows * columns."""
        self.rows = rows_
        self.columns = columns_
        self.grid_x = self.x + self.X_MARGIN + padding
        self.grid_y = self.y + self.Y_MARGIN + self.Y_SHIFT + self.HEADER_HEIGHT + padding
        self.tile_width = (self.width - 2 * (self.X_MARGIN + padding))/self.columns
        self.tile_height = (self.height - self.HEADER_HEIGHT - self.Y_SHIFT - 2 * (self.Y_MARGIN + padding))/self.rows

    def placeControl(self, control, row, column, rowspan=1, columnspan=1, padding=5):
        """Place control within the window grid layout."""
        control_x = (self.grid_x + self.tile_width * column) + padding
        control_y = (self.grid_y + self.tile_height * row) + padding
        control_width = self.tile_width * columnspan - 2 * padding
        control_height = self.tile_height * rowspan - 2 * padding
        control.setPosition(control_x, control_y)
        control.setWidth(control_width)
        control.setHeight(control_height)
        self.addControl(control)

    def getX(self):
        """Get X coordinate of the top-left corner of the window."""
        return self.x

    def getY(self):
        """Get Y coordinate of the top-left corner of the window."""
        return self.y

    def getWindowWidth(self):
        """Get window width."""
        return self.width

    def getWindowHeight(self):
        """Get window height."""
        return self.height

    def setTitle(self, title=''):
        """
        Set window title.

        This method must be called *after* (!!!) setGeometry(),
        otherwise there is some werid bug with all skin text labels set to 'title' text.
        """
        self.title_bar.setLabel(title)

    def getTitle(self):
        """Get windos title."""
        return self.title_bar.getLabel()

    def getRows(self):
        """Get grid rows count."""
        return self.rows

    def getColumns(self):
        """Get grid columns count."""
        return self.columns

    def onAction(self, action):
        """
        Catch button actions.

        Note that, despite being compared to an integer,
        action is an instance of xbmcgui.Action class.
        """
        if action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK:
            self.close()

class AddonDialogWindow(xbmcgui.WindowDialog, AddonWindow):

    """
    Addon UI container with a transparent background.

    Control window is displayed on top of XBMC UI,
    including video an music visualization!
    This abstract class is not supposed to be instantiated directly
    and will raise NotImplementedError exeption!
    """

    def __init__(self, title=''):
        AddonWindow.__init__(self, title)


class AddonFullWindow(xbmcgui.Window, AddonWindow):

    """
    Addon UI container with a solid background.

    Control window is displayed on top of the main background image.
    Video and music visualization are displayed unhindered.
    This abstract class is not supposed to be instantiated directly
    and will raise NotImplementedError exeption!
    """

    def __init__(self, title=''):
        """Constructor method."""
        AddonWindow.__init__(self, title)
        #self.main_bg = xbmcgui.ControlImage(0, 0, 1280, 720, self.main_bg_img)
        #self.addControl(self.main_bg)

    def setImages(self):
        """
        Set images.
        This method must be fully implemented in a child class
        with a full paths to self.main_bg_img and other images for Control window.
        """
        # Main background image
        self.main_bg_img = 'SKINDEFAULT.jpg'
        AddonWindow.setImages(self)


def main():
    pass

if __name__ == '__main__':
    main()
