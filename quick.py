from asyncio.subprocess import PIPE
from os import system
import gi
import os
import subprocess
import argparse

import yt_dlp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Downloader:
    def __init__(self, ytdl_bin_path: str, out_basepath: str):
        self.ytdl_bin_path = ytdl_bin_path
        self.out_basepath = out_basepath
    
    #returns (successful, error-from-stderr)
    def download(self,uri: str, file_name: str) -> tuple[bool, str]:
        proc = subprocess.Popen(
            [self.ytdl_bin_path, "-i", uri, "-o", f"{self.out_basepath}{os.sep}{file_name}"],
            stderr=subprocess.PIPE
        )
        _, stderr = proc.communicate()
        code = proc.wait()
        return (True, None) if code == 0 else (False, stderr.decode("utf-8"))

class GuiWin(Gtk.Window):
    def __init__(self, downloader, file_exts):
        self.downloader = downloader
        self.init_gui(file_exts)
    def init_gui(self, file_exts):
        super().__init__(title="Quick Download")

        self.input_box = Gtk.Box(spacing=2)
        self.add(self.input_box)

        self.url_input = Gtk.Entry()
        self.url_input.set_placeholder_text("meme.site/funny.mp4")
        self.input_box.pack_start(self.url_input, True, True, 0)

        self.file_name_input = Gtk.Entry()
        self.file_name_input.set_placeholder_text("funny-file-name")
        self.input_box.pack_start(self.file_name_input, True, True, 0)

        self.extension_select = Gtk.ComboBoxText()
        #self.extension_select.set_title("ext")
        for ext in file_exts:
            self.extension_select.append(ext, ext)
        self.extension_select.set_active(0)
        self.input_box.pack_start(self.extension_select, True, True, 0)

        self.go_button = Gtk.Button(label="go")
        self.go_button.connect("clicked", self.download)
        self.input_box.pack_start(self.go_button, True, True, 0)

        self.spinner = Gtk.Spinner()
        self.input_box.pack_start(self.spinner, True, True, 0)

    def lock_inputs(self):
        self.input_box.set_sensitive(False)
    #returns (url,file-name, extension)
    def fetch_params(self)->tuple[str,str,str]:
        return (self.url_input.get_text(), self.file_name_input.get_text(), self.extension_select.get_active_id())
    
    def display_error(self, msg: str):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=msg,
        )
        dialog.run()
        dialog.destroy()
    def download(self, w):
        self.spinner.start()
        uri, file_name, ext = self.fetch_params()
        self.lock_inputs()
        
        success, err = self.downloader.download(uri,f"{file_name}.{ext}")
        if not success:
            self.display_error(err)
        Gtk.main_quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='download shitposts quickly')
    parser.add_argument("--yt-dlp-bin", type=str, help="path to your youtube-dl or yt-dlp binary", default="/usr/bin/yt-dlp")
    parser.add_argument("--output-path", type=str, help="where to dump your shitty videos", required=True)
    parser.add_argument("--ext", type=str, action='append', help="add a file extension")
    args = parser.parse_args()

    win = GuiWin(Downloader(args.yt_dlp_bin, args.output_path), args.ext)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()