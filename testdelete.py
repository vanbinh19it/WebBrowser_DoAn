import sys
import json
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
    QMessageBox,
)

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QDesktopServices


import requests


# from pytube import YouTube

# download video youtube


class CustomWebEnginePage(QWebEnginePage):
    """Custom WebEnginePage to customize how we handle link navigation"""

    # Store external windows.
    external_windows = []

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        print(
            f"Accepting navigation request. URL: {url}, Type: {_type}, isMainFrame: {isMainFrame}"
        )

        if "youtube.com" in url.toString():
            # Do something different, maybe open it in the default browser or handle separately
            print("YouTube video link detected. Skipping loading.")
            return False

        # Your existing logic

        if (
            _type == QWebEnginePage.NavigationTypeLinkClicked
            and url.host() != "http://google.com"
        ):
            # Pop up external links into a new window.
            w = QWebEngineView()
            w.setUrl(url)
            # w.show()
            w = None
            # Check if the link is meant to be opened in the same window
            if isMainFrame:
                # Load the link in the current window
                self.parent().browser.setUrl(url)
            else:
                # Open external links in a new window.
                w = QWebEngineView()
                w.setUrl(url)
                w.show()

            # Keep reference to external window, so it isn't cleared up.
            self.external_windows.append(w)
            return False

        return super().acceptNavigationRequest(url, _type, isMainFrame)

    # def acceptNavigationRequest(self, url, _type, isMainFrame):
    #     print(url, _type, isMainFrame)
    #     if _type == QWebEnginePage.NavigationTypeLinkClicked:
    #         if not self.external_window:
    #             self.external_window = QWebEngineView()

    #         self.external_window.setUrl(url)
    #         self.external_window.show()
    #         return False

    #     return super().acceptNavigationRequest(url, _type, isMainFrame)


class CustomApplication(QApplication):
    def notify(self, receiver, event):
        try:
            return super().notify(receiver, event)
        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(None, "Error", f"An error occurred: {e}")
            return False


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        super(MainWindow, self).__init__()

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self))
        self.setCentralWidget(self.browser)
        self.browser.setUrl(QUrl("http://google.com"))

        self.browser.urlChanged.connect(
            self.handle_url_change
        )  # Connect to a new method

        self.history = []
        self.extensions = []
        self.setCentralWidget(self.browser)
        self.showMaximized()
        self.bookmarks = []
        self.load_bookmarks()

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

        # Create bookmark action and add it to the toolbar
        bookmark_btn = QAction("Bookmark", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)

        # Create bookmark list widget
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.open_bookmark)

        # Corrected method name
        show_bookmarks_btn = QAction("Show Bookmarks", self)
        show_bookmarks_btn.triggered.connect(self.show_bookmarks_dialog)
        navbar.addAction(show_bookmarks_btn)

        # Create delete bookmark action and add it to the toolbar
        delete_bookmark_btn = QAction("Delete Bookmark", self)
        delete_bookmark_btn.triggered.connect(self.delete_bookmark)
        navbar.addAction(delete_bookmark_btn)

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

        # download_btn = QAction("Download Video", self)
        # download_btn.triggered.connect(self.download_video)
        # navbar.addAction(download_btn)

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

    def handle_url_change(self, q):
        new_url = q.toString()
        print(f"URL changed to: {new_url}")

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://google.com"))

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
        # def download_video(self):
        # current_url = self.browser.url().toString()
        # if "youtube.com" in current_url:
        #     try:
        #         yt = YouTube(current_url)
        #         video_stream = yt.streams.get_highest_resolution()
        #         save_path = (
        #             "your_directory"  # Thay thế bằng đường dẫn thư mục lưu trữ thực tế
        #         )
        #         video_stream.download(output_path=save_path)
        #         print("Video đã được tải xuống thành công.")
        #     except Exception as e:
        #         print(f"Lỗi: {e}")
        # else:
        #     print("Không thể tải video từ trang web khác YouTube.")

    def open_url(self, url):
        self.browser.setUrl(QUrl(url))

    def update_browser_url(self, url):
        self.browser.setUrl(QUrl(url))

    # add bookmarks
    def add_bookmark(self):
        current_url = self.browser.url().toString()
        title, ok = QInputDialog.getText(
            self, "Add Bookmark", "Enter a title for the bookmark:"
        )
        if ok and title:
            bookmark = {"title": title, "url": current_url}
            self.bookmarks.append(bookmark)
            QMessageBox.information(
                self, "Bookmark Added", "Bookmark added successfully."
            )
            self.save_bookmarks()

    def edit_bookmark(self):
        current_item = self.bookmarks_list.currentItem()
        if current_item:
            current_index = self.bookmarks_list.row(current_item)
            current_url = self.browser.url().toString()
            title, ok = QInputDialog.getText(
                self,
                "Edit Bookmark",
                "Enter a new title for the bookmark:",
                text=current_item.text(),
            )
            if ok and title:
                self.bookmarks[current_index]["title"] = title
                self.bookmarks[current_index]["url"] = current_url
                QMessageBox.information(
                    self, "Bookmark Updated", "Bookmark updated successfully."
                )
                self.save_bookmarks()

    # def delete_bookmark(self):
    #     current_item = self.bookmarks_list.currentItem()
    #     if current_item:
    #         current_index = self.bookmarks_list.row(current_item)
    #         title = current_item.text()
    #         reply = QMessageBox.question(
    #             self,
    #             "Delete Bookmark",
    #             f"Are you sure you want to delete the bookmark '{title}'?",
    #             QMessageBox.Yes | QMessageBox.No,
    #             QMessageBox.No,
    #         )

    #         if reply == QMessageBox.Yes:
    #             del self.bookmarks[current_index]
    #             QMessageBox.information(
    #                 self, "Bookmark Deleted", "Bookmark deleted successfully."
    #             )
    #             self.save_bookmarks()
    #             self.refresh_bookmarks_list()
    #         else:
    #             QMessageBox.information(
    #                 self, "Delete Cancelled", "Bookmark deletion cancelled."
    #             )

    def delete_bookmark(self):
        current_item = self.bookmarks_list.currentItem()
        reply = QMessageBox.No  # Initialize with a default value

        if current_item:
            current_index = self.bookmarks_list.row(current_item)
            title = current_item.text()
            reply = QMessageBox.question(
                self,
                "Delete Bookmark",
                f"Are you sure you want to delete the bookmark '{title}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

        if reply == QMessageBox.Yes:
            del self.bookmarks[current_index]
            QMessageBox.information(
                self, "Bookmark Deleted", "Bookmark deleted successfully."
            )
            self.save_bookmarks()
            self.refresh_bookmarks_list()
        else:
            QMessageBox.information(
                self, "Delete Cancelled", "Bookmark deletion cancelled."
            )

    # def delete_bookmark(self):
    #     current_item = self.bookmarks_list.currentItem()
    #     # reply = QMessageBox.No  # Initialize with a default value

    #     if current_item:
    #         current_index = self.bookmarks_list.row(current_item)
    #         title = current_item.text()
    #         reply = QMessageBox.question(
    #             self,
    #             "Delete Bookmark",
    #             f"Are you sure you want to delete the bookmark '{title}'?",
    #             QMessageBox.Yes | QMessageBox.No,
    #             QMessageBox.No,
    #         )

    #         if reply == QMessageBox.Yes:
    #             del self.bookmarks[current_index]
    #             QMessageBox.information(
    #                 self, "Bookmark Deleted", "Bookmark deleted successfully."
    #             )
    #             self.save_bookmarks()

    #             # Cập nhật danh sách bookmark
    #             self.refresh_bookmarks_list()

    #             # Cập nhật QListWidget
    #             self.bookmarks_list.clear()
    #             for bookmark in self.bookmarks:
    #                 if "title" in bookmark:
    #                     self.bookmarks_list.addItem(bookmark["title"])
    #                 else:
    #                     print("Invalid bookmark format:", bookmark)

    def refresh_bookmarks_list(self):
        # Clear the existing items in the list
        self.bookmarks_list.clear()

        # Add bookmarks to the list using 'title' key
        for bookmark in self.bookmarks:
            if "title" in bookmark:
                self.bookmarks_list.addItem(bookmark["title"])
            else:
                print("Invalid bookmark format:", bookmark)

    def show_bookmarks_dialog(self):
        bookmarks_dialog = BookmarksDialog(self.bookmarks, parent=self)
        bookmarks_dialog.bookmark_selected.connect(self.open_bookmark)
        bookmarks_dialog.exec_()

        # Kiểm tra xem người dùng đã đóng hộp thoại hay chưa

        if bookmarks_dialog.exec_() == QDialog.Accepted:
            # Cập nhật danh sách bookmark
            self.refresh_bookmarks_list()

            # Cập nhật QListWidget
            self.bookmarks_list.clear()
            for bookmark in self.bookmarks:
                if "title" in bookmark:
                    self.bookmarks_list.addItem(bookmark["title"])
                else:
                    print("Invalid bookmark format:", bookmark)

        # else:
        #     QMessageBox.information(
        #         self, "Delete Cancelled", "Bookmark deletion cancelled."
        #     )

    def open_bookmark(self, url):
        self.browser.setUrl(QUrl(url))

    def load_bookmarks(self):
        # Load bookmarks from a file (if the file exists)
        try:
            with open("bookmarks.json", "r") as file:
                data = file.read()
                if data:
                    self.bookmarks = json.loads(data)
                else:
                    self.bookmarks = []  # Provide a default value
        except FileNotFoundError:
            self.bookmarks = []  # Provide a default value if the file doesn't exist

    def save_bookmarks(self):
        # Save bookmarks to a file
        with open("bookmarks.json", "w") as file:
            json.dump(self.bookmarks, file)


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


class BookmarksDialog(QDialog):
    bookmark_selected = pyqtSignal(str)

    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        layout = QVBoxLayout()

        self.bookmarks_list = QListWidget()

        # Add bookmarks to the list using 'title' key
        for bookmark in bookmarks:
            if "title" in bookmark:
                self.bookmarks_list.addItem(bookmark["title"])
            else:
                print("Invalid bookmark format:", bookmark)

        # Connect itemDoubleClicked signal to the slot that emits bookmark_selected
        self.bookmarks_list.itemDoubleClicked.connect(self.emit_bookmark_selected)

        layout.addWidget(self.bookmarks_list)
        self.setLayout(layout)

    def emit_bookmark_selected(self, item):
        selected_index = self.bookmarks_list.row(item)
        selected_url = self.parent().bookmarks[selected_index]["url"]
        self.bookmark_selected.emit(selected_url)


app = QApplication(sys.argv)
QApplication.setApplicationName("Sagar's Browser")
window = MainWindow()
# window.show()
app.exec_()
