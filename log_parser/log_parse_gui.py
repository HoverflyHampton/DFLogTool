from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.popup import Popup

from log_parser.DFParser import DFLog

import os

def loadFolder(folder):
    files = [os.path.join(folder, file) for file in os.listdir(
        folder) if file.lower().endswith('bin') or file.lower().endswith('log')]
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

def parse(base, sync, other, offset):
    if base is None:
        return None
    log = DFLog(base)
    ts = offset
    if sync is not None:
        ips_log = DFLog(sync)
        ts += log.find_offset(ips_log)
        log.merge(ips_log, drop_tables=['GPS'], time_shift=ts)
    if other is not None:
        for f in other:
            log.merge(DFLog(f), drop_tables=['GPS'], time_shift=ts)
    return log

class LoadBaseDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class LoadSyncDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class LoadOtherDialog(FloatLayout):
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
    displayText = ObjectProperty("Select a folder to load files from before saving - no folder currently selected")
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_base_load(self):
        content = LoadBaseDialog(load=self.load_base, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select Folder", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_sync_load(self):
        content = LoadSyncDialog(load=self.load_sync, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select Folder", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_other_load(self):
        content = LoadOtherDialog(load=self.load_other, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select Folder", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load_base(self, path, filename):
        print(path, filename)
        self.base = os.path.join(path, filename[0])
        self.update_display()
        self.dismiss_popup()

    def load_sync(self, path, filename):
        self.sync = os.path.join(path, filename[0])
        self.update_display()
        self.dismiss_popup()

    def load_other(self, path, filenames):
        self.other = []
        for name in filenames:
            self.other.append(os.path.join(path, name))
        self.update_display()
        self.dismiss_popup()

    def update_display(self):
        self.displayText = "Base: {}\nSync: {}\nOther Files: \n".format(
            self.base, self.sync)
        otherText = '             {}\n'*len(self.other)
        self.displayText += otherText.format(*self.other)
    
    
    # def load(self, path, filename):
    #     folder = filename[0]
    #     self.base, self.sync, self.other = loadFolder(folder)
    #     print(self.base, self.sync, self.other)
    #     self.displayText = "Base: {}\nSync: {}\nOther Files: \n".format(self.base, self.sync)
    #     otherText = '             {}\n'*len(self.other)
    #     self.displayText += otherText.format(*self.other)
    #     print(self.displayText)
    #     self.dismiss_popup()

    def save(self, path, filename):
        self.displayText = "Processing..."
        self.dismiss_popup()
        offset = 0
        try:
            offset = int(self.ids.time_offset.text)
        except:
            pass
        print(offset)
        log = parse(self.base, self.sync, self.other, offset)
        
        if log is not None:
            if filename == "":
                filename = "combo.log"
            fh = os.path.join(path, filename)
            log.output_log(fh)
            self.displayText = "Merged File Saved"
        else:
            "Unknown Error : Merge file not saved"
        

class Editor(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadBaseDialog', cls=LoadBaseDialog)
Factory.register('LoadSyncDialog', cls=LoadSyncDialog)
Factory.register('LoadOtherDialog', cls=LoadOtherDialog)
Factory.register('SaveDialog', cls=SaveDialog)

def main():
    Editor().run()

if __name__ == '__main__':
    Editor().run()
