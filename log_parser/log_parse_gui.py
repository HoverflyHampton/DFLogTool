from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.popup import Popup

from log_parser.DFParser import DFLog

import os

def loadFolder(folder):
    files = [os.path.join(folder, file) for file in os.listdir(
        folder) if file.endswith('bin') or file.endswith('log')]
    base_file = None
    sync_file = None
    other_files = []
    for f in files:
        if 'HUE' in f:
            sync_file = f
        elif 'PIX' in f:
            base_file = f
        else:
            other_files.append(f)
    return (base_file, sync_file, other_files)

def parse(base, sync, other):
    if base is None:
        return None
    log = DFLog(base)
    ts = 0
    if sync is not None:
        ips_log = DFLog(sync)
        ts += log.find_offset(ips_log)
        log.merge(ips_log, drop_tables=['GPS'], time_shift=ts)
    if other is not None:
        for f in other:
            log.merge(DFLog(f), drop_tables=['GPS'], time_shift=ts)
    return log

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    base = ObjectProperty(None)
    sync = ObjectProperty(None)
    other = ListProperty([])
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select Folder", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def load(self, path, filename):
        folder = filename[0]
        self.base, self.sync, self.other = loadFolder(folder)
        self.dismiss_popup()

    def save(self, path, filename):
        print(path, filename)
        log = parse(self.base, self.sync, self.other)
        
        if log is not None:
            fh = os.path.join(path, filename)
            log.output_log(fh)
        self.dismiss_popup()


class Editor(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

def main():
    Editor().run()

if __name__ == '__main__':
    Editor().run()
