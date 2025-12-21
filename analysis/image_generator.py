import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import exporters
from PySide6.QtGui import QColor, QPicture, QPainter, QBrush
from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtWidgets import QApplication

# Ensure a QApplication instance exists for rendering
app = QApplication.instance()
if app is None:
    app = QApplication([])

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data, style):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.style = style
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        w = self.style.get('bar_width', 5) / 10.0
        
        for item in self.data:
            t, o, h, l, c = item['t'], item['open'], item['high'], item['low'], item['close']
            prev_close = item.get('prev_close')

            p.setPen(pg.mkPen(color=self.style.get('line_color', 'w'), width=self.style.get('line_width', 1)))
            p.drawLine(QPointF(t, l), QPointF(t, h))
            
            # Determine color based on open vs close
            color = QColor(self.style.get('up_color', 'g')) if c > o else QColor(self.style.get('down_color', 'r'))
            p.setPen(pg.mkPen(color, width=self.style.get('border_thickness', 1)))

            # Determine fill based on chart type
            is_hollow = False
            if self.style.get('chart_type') == 'Hollow Candlestick' and prev_close is not None:
                if c > prev_close:
                    is_hollow = True
            
            if is_hollow:
                p.setBrush(QBrush(Qt.NoBrush))
            else:
                p.setBrush(color)
            
            p.drawRect(QRectF(t - w / 2, o, w, c - o))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

class ImageGenerator:
    def __init__(self, config):
        self.config = config
        self.chart_type = config.get("chart_type", "Candlestick")
        self.style_params = config.get("style_settings", {})
        self.width = self.style_params.get("target_width", 128)
        self.height = self.style_params.get("target_height", 64)
        self.bg_color = self.style_params.get("bg_color", "#2d2d2d")

    def _heikin_ashi(self, df):
        ha_df = df.copy()
        ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_df['ha_open'] = np.nan
        ha_df.loc[0, 'ha_open'] = (df.loc[0, 'open'] + df.loc[0, 'close']) / 2
        for i in range(1, len(df)):
            ha_df.loc[i, 'ha_open'] = (ha_df.loc[i-1, 'ha_open'] + ha_df.loc[i-1, 'ha_close']) / 2
        ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
        ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)
        return ha_df.rename(columns={'ha_open': 'open', 'ha_high': 'high', 'ha_low': 'low', 'ha_close': 'close'})

    def _renko(self, df):
        from stocktrends import Renko
        renko_df = Renko(df)
        renko_df.set_brick_size(auto = True)
        return renko_df.get_ohlc_data()

    def _draw_overlays(self, plot_item, df):
        overlays_config = self.style_params.get('overlays', {})
        if overlays_config.get('moving_average', {}).get('enabled'):
            period = overlays_config['moving_average'].get('period', 20)
            ma = df['close'].rolling(window=period).mean().values
            plot_item.plot(np.arange(len(ma)), ma, pen=pg.mkPen('c', width=1))

    def generate_image(self, df):
        if df.empty:
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)

        glw = pg.GraphicsLayoutWidget(show=False, size=(self.width, self.height))
        glw.setBackground(self.bg_color)

        volume_display = self.style_params.get('volume_display', 'None')
        price_plot = glw.addPlot(row=0, col=0)
        if volume_display == 'Bottom Subplot':
            glw.ci.layout.setRowStretchFactor(0, 3)
            volume_plot = glw.addPlot(row=1, col=0)
            glw.ci.layout.setRowStretchFactor(1, 1)
            volume_plot.setXLink(price_plot)
        
        for plot in [price_plot] + ([volume_plot] if volume_display == 'Bottom Subplot' else []):
            plot.hideAxis('left'); plot.hideAxis('bottom')
            plot.setMouseEnabled(x=False, y=False); plot.setMenuEnabled(False)
            plot.setClipToView(True)

        # --- Price Plot ---
        chart_df = df.copy()
        chart_df['prev_close'] = chart_df['close'].shift(1)

        if self.chart_type == "Heikin-Ashi":
            chart_df = self._heikin_ashi(chart_df)
        elif self.chart_type == "Renko":
            chart_df = self._renko(chart_df)

        item_data = [{'t': i, 'open': row.open, 'high': row.high, 'low': row.low, 'close': row.close, 'prev_close': row.prev_close} for i, row in chart_df.iterrows()]
        
        # Pass chart_type to style_params for CandlestickItem
        style = self.style_params.copy()
        style['chart_type'] = self.chart_type

        if self.chart_type in ["Candlestick", "Heikin-Ashi", "Hollow Candlestick", "Renko"]:
            if self.chart_type == "Renko":
                for d in item_data:
                    d['high'] = max(d['open'], d['close'])
                    d['low'] = min(d['open'], d['close'])
            plot_graphic = CandlestickItem(item_data, style)
        elif self.chart_type == "Line":
            plot_graphic = pg.PlotDataItem([d['t'] for d in item_data], [d['close'] for d in item_data], pen=pg.mkPen(color=style.get('line_color', 'w'), width=style.get('line_width', 2)))
        else:
            plot_graphic = CandlestickItem(item_data, style)
        
        price_plot.addItem(plot_graphic)
        self._draw_overlays(price_plot, df)
        price_plot.autoRange()

        # --- Volume Plot ---
        if volume_display == 'Bottom Subplot':
            up_color = QColor(self.style_params.get('up_color', '#26a69a')); up_color.setAlpha(150)
            down_color = QColor(self.style_params.get('down_color', '#ef5350')); down_color.setAlpha(150)
            colors = [up_color if c > o else down_color for o, c in zip(df['open'], df['close'])]
            volume_plot.addItem(pg.BarGraphItem(x=np.arange(len(df)), height=df['volume'].values, width=0.8, brushes=colors))
            volume_plot.autoRange()

        # --- Export ---
        exporter = exporters.ImageExporter(glw.scene())
        image = exporter.export(toBytes=True)
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        arr = np.array(ptr).reshape(image.height(), image.width(), 4)
        arr = arr[..., :3][..., ::-1]
        glw.close()
        
        return arr

    def _log(self, message, level='info'):
        print(f"[{level.upper()}] ImageGenerator: {message}")