import os
import threading
import webbrowser

import markdown
import webview


def show_md_from_file(file_path):
    # Read Markdown content from the file
    with open(file_path, "r") as file:
        md_content = file.read()

    # Convert Markdown content to HTML
    html_content = markdown.markdown(md_content)

    # Create a webview window to display the HTML content
    webview.create_window("Help Documentation", html=html_content)
    webview.start()
