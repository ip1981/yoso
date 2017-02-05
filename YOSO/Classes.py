from PyQt5.QtCore import ( QAbstractListModel, QMimeData,
                           QModelIndex, Qt, QVariant )



class Class:
    _image = None
    _name = None
    _number = None

    def __init__(self, number, name, image):
        self._image = image
        self._name = name
        self._number = number

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    @property
    def image(self):
        return self._image

    @property
    def display(self):
        return '{} - {}'.format(self._number, self._name)


class ClassListModel(QAbstractListModel):

    _classes = None
    _size = 0

    def __init__(self, classes, parent=None):
        super().__init__(parent)
        self._classes = dict(enumerate(classes))
        self._size = len(self._classes)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled

    def rowCount(self, parent=QModelIndex()):
        return len(self._classes)

    def mimeTypes(self):
        return 'text/plain'

    def mimeData(self, indeces):
        idx = indeces[0]
        cls = idx.data(Qt.UserRole)
        mime_data = QMimeData()
        mime_data.setText(str(cls))
        return mime_data

    def data(self, index, role):
        if index.isValid():
            cl = self._classes[index.row()]
            if role == Qt.DisplayRole:
                return QVariant(cl.display)
            if role == Qt.DecorationRole:
                return QVariant(cl.image)
            if role == Qt.UserRole:
                return QVariant(cl.number)
        return QVariant()

    def findClass(self, num):
        for i in range(self._size):
            if self._classes[i].number == num:
                return self.index(i, 0)
        return QModelIndex()

    @property
    def classes(self):
        return self._classes

    def hsvF(self, num):
        hue = 0.1 
        if self._size > 0:
            hue += num / self._size
        sat = 1.0
        val = 1.0
        return (hue, sat, val)


