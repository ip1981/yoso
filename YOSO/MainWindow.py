from os import makedirs
from os.path import basename
import errno

from PyQt5.QtCore import QDir, QDirIterator, QItemSelectionModel, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import ( QAction, QComboBox, QFileDialog,
    QListView, QMainWindow, QProgressBar, QSpinBox, QSplitter, QVBoxLayout,
    QWidget, qApp )

from YOSO.Classes import Class, ClassListModel
from YOSO.Workspace import Workspace
import YOSO

class MainWindow(QMainWindow):

    _classes_view = None
    _current_images = []
    _image_dirs_combo_box = None
    _image_spinner = None
    _next_image_action = None
    _prev_image_action = None
    _progress_bar = None
    _top_images_dir = None
    _top_labels_dir = None
    _workspace = None

    def openImages(self, directory):
        image_it = QDirIterator(directory, YOSO.IMAGE_FILE_TEMPLATES,
                QDir.Files, QDirIterator.Subdirectories)
        self._current_images = []
        while image_it.hasNext():
            self._current_images.append(image_it.next())
        self._current_images.sort()

        self._image_spinner.setRange(0, 0)
        self._image_spinner.setEnabled(False)
        self._image_spinner.setValue(0)
        image_total = len(self._current_images)
        if image_total > 0:
            self._progress_bar.setRange(0, image_total)
            self._image_spinner.setRange(1, image_total)
            self._image_spinner.setEnabled(True)
            self._image_spinner.setValue(1)


    def openDataDir(self):
        dialog = QFileDialog(self)

        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ReadOnly)

        if dialog.exec():
            datadir = dialog.selectedFiles()[0]

            classesdir = YOSO.classesDir(datadir)
            classesdir_it = QDirIterator(classesdir, YOSO.IMAGE_FILE_TEMPLATES, QDir.Files)
            classes = []
            while classesdir_it.hasNext():
                class_image = classesdir_it.next()
                match = YOSO.CLASSES_RE.match(basename(class_image))
                if match != None:
                    class_num = int(match.group('cls'))
                    class_name = match.group('name')
                    class_object = Class(class_num, class_name, QPixmap(class_image))
                    classes.append(class_object)
            classes.sort(key = lambda c: c.number)

            classes_model = ClassListModel(classes)
            self._classes_view.setModel(classes_model)
            self._workspace.setModel(classes_model)
            self._classes_view.setEnabled(len(classes) > 0)
            selMod = self._classes_view.selectionModel()
            selMod.currentChanged.connect(self._workspace.setDefaultClass)
            selMod.setCurrentIndex(classes_model.index(0, 0), QItemSelectionModel.Select)

            self._top_images_dir = YOSO.imagesDir(datadir)
            self._top_labels_dir = YOSO.labelsDir(datadir)

            imagedir_it = QDirIterator(self._top_images_dir,
                    QDir.AllDirs | QDir.NoDotAndDotDot, QDirIterator.Subdirectories)
            self._image_dirs_combo_box.clear()
            self._image_dirs_combo_box.addItem(self._top_images_dir)
            while imagedir_it.hasNext():
                img_dir = imagedir_it.next()
                self._image_dirs_combo_box.addItem(img_dir)
                lbl_dir = img_dir.replace(self._top_images_dir, self._top_labels_dir)
                try:
                    makedirs(lbl_dir)
                except OSError as ex:
                    if ex.errno != errno.EEXIST:
                        raise


    def loadImage(self, i):
        self._prev_image_action.setEnabled(i > 1)
        self._next_image_action.setEnabled(i < self._image_spinner.maximum())
        if 1 <= i <= self._image_spinner.maximum():
            image_path = self._current_images[i - 1]
            label_path = image_path.replace(self._top_images_dir, self._top_labels_dir) + '.txt'
            self._workspace.loadImage(image_path, label_path)


    def nextImage(self):
        self._image_spinner.setValue(self._image_spinner.value() + 1)

    def prevImage(self):
        self._image_spinner.setValue(self._image_spinner.value() - 1)


    def __init__(self):
        super().__init__()

        self.setWindowTitle('YOSO - You Only Show Once')
        self.resize(800, 600)
        self.move(qApp.desktop().availableGeometry().center() - self.frameGeometry().center())


        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Q')
        quit_action.setStatusTip('Quit application')
        quit_action.triggered.connect(qApp.quit)

        open_action = QAction('&Open', self)
        open_action.setShortcut('O')
        open_action.setStatusTip('Open data directory')
        open_action.triggered.connect(self.openDataDir)

        self._prev_image_action = QAction('Prev (&A)', self)
        self._prev_image_action.setEnabled(False)
        self._prev_image_action.setShortcut('A')
        self._prev_image_action.setStatusTip('Show previous image')
        self._prev_image_action.triggered.connect(self.prevImage)

        self._next_image_action = QAction('Next (&D)', self)
        self._next_image_action.setEnabled(False)
        self._next_image_action.setShortcut('D')
        self._next_image_action.setStatusTip('Show next image')
        self._next_image_action.triggered.connect(self.nextImage)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        menubar.addAction(open_action)
        menubar.addSeparator()
        menubar.addAction(self._prev_image_action)
        menubar.addAction(self._next_image_action)
        menubar.addSeparator()
        menubar.addAction(quit_action)


        statusbar = self.statusBar()
        self._progress_bar = QProgressBar()
        self._progress_bar.setFormat('%p% of %m')
        self._image_spinner = QSpinBox()
        self._image_spinner.setEnabled(False)
        self._image_spinner.valueChanged.connect(self.loadImage)
        self._image_spinner.valueChanged.connect(self._progress_bar.setValue)
        statusbar.addWidget(self._image_spinner)
        statusbar.addWidget(self._progress_bar)
        statusbar.show()


        main_split = QSplitter(Qt.Horizontal)

        left_side = QWidget(main_split)
        right_side = QWidget(main_split)

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        right_side.setLayout(right_layout)
        left_side.setLayout(left_layout)

        self._workspace = Workspace()
        self._classes_view = QListView()
        self._classes_view.setEnabled(False)
        self._classes_view.setDragEnabled(True)
        right_layout.addWidget(self._classes_view)
        left_layout.addWidget(self._workspace)

        self._image_dirs_combo_box = QComboBox()
        left_layout.addWidget(self._image_dirs_combo_box)
        self._image_dirs_combo_box.currentTextChanged.connect(self.openImages)


        main_split.setStretchFactor(0, 1)
        main_split.setStretchFactor(1, 0)

        self.setCentralWidget(main_split)


