import errno
import os

import YOSO

from PyQt5.QtCore import (pyqtSlot, QIODevice,
                          QModelIndex, QPointF, QRectF, QSaveFile, Qt)
from PyQt5.QtGui import QColor, QPen, QPixmap, QTransform
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsRectItem,
                             QGraphicsScene, QGraphicsView)

BBOX = QGraphicsItem.UserType + 1

def _mkRectF(p1, p2):
    rect = QRectF(p1.x(), p1.y(), p2.x() - p1.x(), p2.y() - p1.y())
    return rect.normalized()

class BoundingBoxItem(QGraphicsRectItem):
    _cls = None

    def __init__(self, cls, rect, model):
        super().__init__(rect)
        self._setClass(cls, model)
        self.setAcceptDrops(True)

    @property
    def number(self):
        return self._cls

    def type(self):
        return BBOX

    def _setClass(self, cls, model):
        self._cls = cls
        idx = model.findClass(self._cls)
        (hue, sat, val) = model.hsvF(self._cls)
        pen = QPen(QColor.fromHsvF(hue, sat, val, 0.6), 3)
        self.setPen(pen)
        if idx.isValid():
            self.setToolTip(idx.data(Qt.DisplayRole))
        else:
            self.setToolTip('{} - <unknown>'.format(cls))

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        cls = int(event.mimeData().text())
        self._setClass(cls, self.scene().model)
        self.scene().saveLabels()
        event.accept()


class Scene(QGraphicsScene):

    _bbox_pen = None
    _bbox_start_pos = None
    _default_class = None
    _guide_pen = None
    _image = None
    _img_h = None
    _img_w = None
    _label_path = None
    _model = None
    _mouse_pos = None

    def __init__(self, parent):
        super().__init__(parent)
        self._guide_pen = QPen(Qt.black, 1)
        self.setDefaultClass(0)

    def _boxes(self):
        return list(filter(lambda i: i.type() == BBOX, self.items()))

    def saveLabels(self):
        if self._label_path != None:
            if len(self._boxes()) == 0:
                print('Removing empty "{}"'.format(self._label_path))
                try:
                    os.remove(self._label_path)
                except OSError as ex:
                    if ex.errno != errno.ENOENT:
                        raise
            else:
                lf = QSaveFile(self._label_path)
                if not lf.open(QIODevice.WriteOnly | QIODevice.Text):
                    raise IOError('Cannot open "{}" for writing'.format(self._label_path))

                for bbox in self._boxes():
                    rect = bbox.rect()
                    c = bbox.number
                    x = (rect.x() + rect.width()  / 2) / self._img_w
                    y = (rect.y() + rect.height() / 2) / self._img_h
                    w = rect.width()  / self._img_w
                    h = rect.height() / self._img_h
                    line = '{c:d} {x:.10f} {y:.10f} {w:.10f} {h:.10f}\n'.format(c=c, x=x, y=y, w=w, h=h)
                    lf.write(line.encode())

                if lf.commit():
                    print('Wrote "{}"'.format(self._label_path))
                else:
                    raise IOError('Cannot write "{}"'.format(self._label_path))

    def _addBBox(self, p1, p2, cls):
        rect = _mkRectF(p1, p2).intersected(QRectF(self._image.rect()))
        square = abs(rect.width() * rect.height())
        if square > 0.0:
            zvalue = 1.0 / square
            bbox = BoundingBoxItem(cls, rect, self._model)
            bbox.setZValue(zvalue)
            self.addItem(bbox)
            return True
        else:
            return False

    def _newBBox(self, p1, p2):
        if self._addBBox(p1, p2, self._default_class):
            self.invalidate()
            self.saveLabels()

    def setDefaultClass(self, cls):
        self._default_class = cls
        if self._model != None:
            (hue, sat, val) = self._model.hsvF(self._default_class)
            self._bbox_pen = QPen(QColor.fromHsvF(hue, sat, val), 2)

    def mouseMoveEvent(self, event):
        self._mouse_pos = event.scenePos()
        self.invalidate()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        self._bbox_start_pos = pos

    def mouseReleaseEvent(self, event):
        if self._bbox_start_pos != None:
            self._newBBox(self._bbox_start_pos, event.scenePos())
            self._bbox_start_pos = None
            self._mouse_pos = None

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if item != None and item.type() == BBOX:
            self.removeItem(item)
            self.invalidate()
            self.saveLabels()

    def drawForeground(self, painter, rect):
        if self._mouse_pos != None:
            if self._bbox_start_pos == None:
                painter.setClipRect(rect)
                painter.setPen(self._guide_pen)
                painter.drawLine(self._mouse_pos.x(), rect.top(), self._mouse_pos.x(), rect.bottom())
                painter.drawLine(rect.left(), self._mouse_pos.y(), rect.right(), self._mouse_pos.y())
            else:
                painter.setPen(self._bbox_pen)
                painter.drawRect(_mkRectF(self._bbox_start_pos, self._mouse_pos))

    def loadImage(self, image_path, label_path):
        self.clear()
        self._image = QPixmap(image_path)
        self._label_path = label_path
        self.setSceneRect(QRectF(self._image.rect()))
        self.addPixmap(self._image)
        lines = []
        self._img_h = self._image.height()
        self._img_w = self._image.width()
        try:
            with open(self._label_path) as lbl:
                lines = lbl.readlines()
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise

        for l in lines:
            m = YOSO.BBOX_RE.match(l)
            if m != None:
                cls = int(m.group('cls'))
                x = float(m.group('x'))
                y = float(m.group('y'))
                h = float(m.group('h'))
                w = float(m.group('w'))
                p1 = QPointF((x - w/2) * self._img_w, (y - h/2) * self._img_h)
                p2 = QPointF((x + w/2) * self._img_w, (y + h/2) * self._img_h)
                self._addBBox(p1, p2, cls)
        self.invalidate()


    @property
    def model(self):
        return self._model

    def setModel(self, model):
        self._model = model
        self.setDefaultClass(0)



class Workspace(QGraphicsView):

    _scene = None

    def __init__(self):
        super().__init__()
        self._scene = Scene(self)
        self.setScene(self._scene)
        self.setMouseTracking(True)
        self.setEnabled(False)

    def _fit(self):
        scene_rect = self._scene.sceneRect()
        self.fitInView(scene_rect, Qt.KeepAspectRatio)

    @pyqtSlot(QModelIndex, QModelIndex)
    def setDefaultClass(self, curr, _):
        self._scene.setDefaultClass(curr.data(Qt.UserRole))

    def resizeEvent(self, _):
        self._fit()

    def loadImage(self, image_path, label_path):
        self._scene.loadImage(image_path, label_path)
        self._fit()
        self.viewport().update()
        self.setEnabled(True)

    def setModel(self, model):
        self._scene.setModel(model)

