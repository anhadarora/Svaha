
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QFont
import numpy as np

class ConfusionMatrixWidget(QWidget):
    def __init__(self, title="Confusion Matrix"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.plot_widget.setTitle(title)
        self.image_item = pg.ImageItem()
        self.plot_widget.addItem(self.image_item)
        self.plot_widget.getViewBox().setAspectLocked(True)
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('bottom')
        
        self.text_items = []

    def update_data(self, matrix: list):
        if not matrix:
            return

        # Clear old text items
        for text_item in self.text_items:
            self.plot_widget.removeItem(text_item)
        self.text_items.clear()

        matrix = np.array(matrix)
        
        # Set colormap
        cmap = pg.colormap.get('viridis')
        self.image_item.setLookupTable(cmap.getLookupTable())
        self.image_item.setImage(matrix.T) # Transpose for correct orientation

        # Add text labels for each cell
        font = QFont()
        font.setPointSize(12)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                text = str(matrix[i, j])
                text_item = pg.TextItem(text, anchor=(0.5, 0.5), color=(255, 255, 255))
                text_item.setFont(font)
                text_item.setPos(j + 0.5, i + 0.5)
                self.plot_widget.addItem(text_item)
                self.text_items.append(text_item)
        
        # Set axis labels
        axis_font = QFont()
        axis_font.setPointSize(10)
        self.plot_widget.getAxis('left').setTicks([[(i, str(i)) for i in range(matrix.shape[0])]])
        self.plot_widget.getAxis('left').setLabel('True Label')
        self.plot_widget.getAxis('left').show()
        
        self.plot_widget.getAxis('bottom').setTicks([[(i, str(i)) for i in range(matrix.shape[1])]])
        self.plot_widget.getAxis('bottom').setLabel('Predicted Label')
        self.plot_widget.getAxis('bottom').show()

    def clear_plot(self):
        self.image_item.clear()
        for text_item in self.text_items:
            self.plot_widget.removeItem(text_item)
        self.text_items.clear()
