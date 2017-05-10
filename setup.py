from setuptools import setup, find_packages

setup(
    name             = 'YOSO',
    version          = '0.1.1',
    description      = 'You Only Show Once',
    long_description = 'A GUI tool to create training data for YOLO network by Darknet. See <http://pjreddie.com/darknet/yolo/>.',
    author           = 'Igor Pashev',
    author_email     = 'pashev.igor@gmail.com',
    license          = 'WTFPL',
    data_files       = [('', [ 'LICENSE', 'ChangeLog.rst' ])],

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
    ],

    packages = find_packages(),

    install_requires = [ 'PyQt5' ],

    entry_points = {
        'console_scripts': [
            'yoso=YOSO:main',
        ],
    },
)
