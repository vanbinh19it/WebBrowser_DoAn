import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from bs4 import BeautifulSoup
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

# download video youtube


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://google.com"))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        self.history = []
        self.extensions = []
        self.setCentralWidget(self.browser)
        self.showMaximized()

        navbar = QToolBar()
        self.addToolBar(navbar)

        # Tạo menu Bar
        menu_bar = self.menuBar()

        # Tạo menu "Favorites"
        favorites_menu = menu_bar.addMenu("Favorites")

        # Thêm biểu tượng cho các trang web yêu thích
        google_action = QAction("Google", self)
        google_icon = QIcon("./image/google.png")  # Đường dẫn đến biểu tượng của Google
        google_action.setIcon(google_icon)
        google_action.triggered.connect(lambda: self.open_url("http://www.google.com"))
        favorites_menu.addAction(google_action)

        facebook_action = QAction("Facebook", self)
        facebook_icon = QIcon(
            "./image/facebook.jpg"
        )  # Đường dẫn đến biểu tượng của Facebook
        facebook_action.setIcon(facebook_icon)
        facebook_action.triggered.connect(
            lambda: self.open_url("http://www.facebook.com")
        )
        favorites_menu.addAction(facebook_action)

        vku_action = QAction("VKU", self)
        vku_icon = QIcon("./image/logo_vku.svg")  # Đường dẫn đến biểu tượng của Google
        vku_action.setIcon(vku_icon)
        vku_action.triggered.connect(lambda: self.open_url("https://vku.udn.vn/"))
        favorites_menu.addAction(vku_action)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Create a search bar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search)
        navbar.addWidget(self.search_bar)

        search_btn = QAction("Search", self)
        search_btn.triggered.connect(self.search)
        navbar.addAction(search_btn)

        history_action = QAction("History", self)
        history_action.triggered.connect(self.show_history)
        navbar.addAction(history_action)

        download_btn = QAction("Download Video", self)
        download_btn.triggered.connect(self.download_video)
        navbar.addAction(download_btn)

        extensions_action = QAction("Show Extensions", self)
        extensions_action.triggered.connect(self.show_extensions)
        navbar.addAction(extensions_action)  # Correct indentation

        self.get_btn = QAction("GET", self)
        self.get_btn.triggered.connect(self.send_get_request)
        navbar.addAction(self.get_btn)

        self.post_btn = QAction("POST", self)
        self.post_btn.triggered.connect(self.send_post_request)
        navbar.addAction(self.post_btn)

        self.head_btn = QAction("HEAD", self)
        self.head_btn.triggered.connect(self.send_head_request)
        navbar.addAction(self.head_btn)

        self.browser.urlChanged.connect(self.update_url)

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://tiki.vn"))

    def show_history(self):
        history_dialog = HistoryDialog(self.history)
        history_dialog.exec_()

    def show_extensions(self):
        extensions_dialog = ExtensionsDialog(self.extensions)
        extensions_dialog.exec_()

    def load_extensions(self):
        pass

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))
        self.history.append(url)

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def send_get_request(self):
        url = self.browser.url().toString()
        response = requests.get(url)
        self.display_response_info(response)
        self.analyze_html_content(response.text)

    def send_post_request(self):
        url = self.browser.url().toString()
        response = requests.post(url)
        self.display_response_info(response)
        self.analyze_html_content(response.text)

    def send_head_request(self):
        url = self.browser.url().toString()
        response = requests.head(url)
        self.display_response_info(response)

    def display_response_info(self, response):
        print("Request Response:")
        print("Status Code:", response.status_code)
        print("Content Length:", response.headers.get("Content-Length"))
        print("Content Type:", response.headers.get("Content-Type"))
        print()

    def analyze_html_content(self, html):
        soup = BeautifulSoup(html, "html.parser")

        p_tags = soup.find_all("p")
        div_tags = soup.find_all("div")
        span_tags = soup.find_all("span")
        img_tags = soup.find_all("img")

        print("HTML Content Analysis:")
        print("Number of <p> tags:", len(p_tags))
        print("Number of <div> tags:", len(div_tags))
        print("Number of <span> tags:", len(span_tags))
        print("Number of <img> tags:", len(img_tags))

    # search google
    def search(self):
        # Get the search query from the search bar
        search_query = self.search_bar.text()
        if search_query:
            # Call the method to perform the search
            self.search_google(search_query)

    def search_google(self, query):
        search_url = f"https://www.google.com/search?q={query}"
        self.browser.setUrl(QUrl(search_url))
        self.history.append(search_url)

    #  Download video youtube
    def download_video(self):
        current_url = self.browser.url().toString()
        if "youtube.com" in current_url:
            try:
                yt = YouTube(current_url)
                video_stream = yt.streams.get_highest_resolution()
                save_path = (
                    "your_directory"  # Thay thế bằng đường dẫn thư mục lưu trữ thực tế
                )
                video_stream.download(output_path=save_path)
                print("Video đã được tải xuống thành công.")
            except Exception as e:
                print(f"Lỗi: {e}")
        else:
            print("Không thể tải video từ trang web khác YouTube.")

    def open_url(self, url):
        self.browser.setUrl(QUrl(url))


# Create a HistoryDialog class for displaying history
class HistoryDialog(QDialog):
    def __init__(self, history):
        super().__init__()
        self.setWindowTitle("History")
        layout = QVBoxLayout()

        self.history_list = QListWidget()
        self.history_list.addItems(history)

        layout.addWidget(self.history_list)
        self.setLayout(layout)


class ExtensionsDialog(QDialog):
    def __init__(self, extensions):
        super().__init__()
        self.setWindowTitle("Extensions")
        layout = QVBoxLayout()

        self.extensions_list = QListWidget()
        for extension in extensions:
            self.extensions_list.addItem(f"{extension.name} - {extension.description}")

        layout.addWidget(self.extensions_list)
        self.setLayout(layout)


app = QApplication(sys.argv)
QApplication.setApplicationName("Sagar's Browser")
window = MainWindow()
app.exec_()
