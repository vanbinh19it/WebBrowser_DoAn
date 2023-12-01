from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from bs4 import BeautifulSoup

from PyQt5.QtWebEngine import QtWebEngine

QtWebEngine.initialize()

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMenu,
    QAction,
    QFileDialog,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QDialog,
)
import requests

from pytube import YouTube