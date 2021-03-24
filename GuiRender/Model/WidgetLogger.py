import logging
import tkinter


class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        super(WidgetLogger, self).__init__()
        self.widget = widget

    def emit(self, record):
        # Append message (record) to the widget
        self.widget.insert(tkinter.END, self.format(record) + '\n')
        # Scroll to the bottom
        self.widget.see(tkinter.END)
