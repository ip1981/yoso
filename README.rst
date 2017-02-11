You Only Show Once
==================

YOSO is a GUI application providing a means of creating training data set for
`YOLO <http://pjreddie.com/darknet/yolo/>`_, a state-of-the-art, real-time object detection system.
It can be useful for other computer vision systems, because I believe that YOLO's
label file format is quite a good and flexible choice.


Requirements
============

YOSO is written in `Python 3 <https://www.python.org/>`_ with
the `PyQt5 <https://www.riverbankcomputing.com/software/pyqt/>`_
application framework. If you have Python 3 and PyQt5 (and subsequently `Qt5 <https://www.qt.io>`_ itself)
installed, you can run YOSO by simply executing ``python3 yoso.py``.
Alternatively you can install YOSO with the `pip <https://pip.pypa.io>`_ package manager
(which can be called ``pip3`` for Python 3).


Data Directory Structure
========================

YOSO should be pointed to a data directory having this structure:

::

  data
  |\_ classes
  |   \_ "0 - roy.jpg"
  |   \_ "1 - poli.jpg"
  |   \_ ...
  |\_ images
  |   |\_ poli
  |   |   \_ poli-001.jpg
  |   |   \_ ...
  |   |   \_ poli-009.jpg
  |   |   \_ ...
  |   |\_ roy
  |   |   \_ roy-1.jpg
  |   |   \_ ...
  |   |   \_ roy-99.jpg
  |   |   \_ ...
  |   \_ ...
   \_ labels
      |\_ poli
      |   \_ poli-001.jpg.txt
      |   \_ ...
      |   \_ poli-009.jpg.txt
      |   \_ ...
      |\_ roy
      |   \_ roy-1.jpg.txt
      |   \_ ...
      |   \_ roy-99.jpg.txt
      |   \_ ...
       \_ ...


``data/classes`` must contain JPEG files describing object classes in format: ``<class number> - <short description>.jpg``

``data/images`` has arbitrary structure and contains JPEG or PNG images (``*.jpg``, or ``*.jpeg``, ``*.png``).
This is a training set of hundreds or thousands of images.

``data/labels`` is managed by YOSO and has the same structure as ``data/images``.
All missed subdirectories will be created automatically.
Note that label files create by YOSO have different naming scheme, so you might have to update
`Darknet <http://pjreddie.com/darknet>`_ sources.


Controls
========

- To add a bounding box select a region with the mouse pointer.
  Newly added bounding box will have object class currently selected
  in the list on the right.

- To delete a bounding box double click on it.

- To change object class drag an item from the list on the right
  and drop it into existing bounding box.

Whenever a bounding box is added, deleted or changed, the result is automatically saved.


Screenshots
===========

.. image:: screenshots/yoso-roy-1.png


Video
=====

https://www.youtube.com/watch?v=upPbaXq8wm0


