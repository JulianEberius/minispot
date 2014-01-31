from objc import IBAction, IBOutlet
from Foundation import NSObject, NSLog
from AppKit import NSBundle, NSFileManager, NSApp, NSImage, NSStatusBar
from os.path import abspath, expanduser, isfile
import objc
import json
import hotkeys
from spotify import Spotify, async_load


def resource_path(resource, resource_type):
        path = NSBundle.mainBundle().pathForResource_ofType_(
            resource, resource_type)
        if NSFileManager.defaultManager().fileExistsAtPath_(path):
                return path
        else:
                return None


class ImageProxy(object):

    def __init__(self, album, img_loaded_cb):
        self.album = album
        self.img_loaded_cb = img_loaded_cb
        self.started_load = False

    def __call__(self):
        if self.album.cover().isLoaded():
            return self.album.cover().image()
        elif not self.started_load:
            self.started_load = True
            async_load(self.album.cover(), self.img_loaded_cb)
        return None


class MiniSpotAppDelegate(NSObject):

    status_menu = IBOutlet()
    search_box = IBOutlet()
    login_window = IBOutlet()
    result_table = IBOutlet()
    search_window = IBOutlet()
    username_box = IBOutlet()
    password_box = IBOutlet()

    def awakeFromNib(self):
        self.state = "album_browsing"
        self.selected_album = None
        self.selected_album_details = None
        self.track_names = []
        self.img_cache = {}
        self.result = []
        self.last_query = None

        # configuration
        self.config = {}
        config_path = abspath(expanduser("~/.minispot"))
        if isfile(config_path):
            with open(config_path) as conf_file:
                self.config = json.load(conf_file)
        else:
            with open(config_path, "w") as conf_file:
                json.dump(self.config, conf_file, indent=4)

        # ui setup
        self._initStatusBarItem()
        self._initTableView()
        NSApp.hide_(None)

        # spotify
        self.spotify = Spotify.alloc().init()
        logged_in = self.spotify.login_saved_credentials()
        if not logged_in:
            self.display_login_window()

        self.addObserver_forKeyPath_options_context_(self, "spotify.login_state", 0, None)
        self.addObserver_forKeyPath_options_context_(self, "spotify.current_track", 0, None)

        # hotkeys
        self.hotkey = hotkeys.register_key_from_string("alt+ctrl+f", self, "focusSearchWindow:")
        self.hotkey = hotkeys.register_key_from_string("alt+ctrl+x", self, "exit:")
        self.hotkey = hotkeys.register_key_from_string("alt+ctrl+n", self, "nextTrack:")
        self.hotkey = hotkeys.register_key_from_string("alt+ctrl+r", self, "previousTrack:")
        self.hotkey = hotkeys.register_key_from_string("alt+ctrl+p", self, "togglePause:")

    def display_login_window(self):
        NSApp.arrangeInFront_(None)
        self.login_window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        self.login_window.makeFirstResponder_(self.username_box)

    """ interface actions """
    @IBAction
    def login_(self, sender):
        username = str(self.username_box.stringValue())
        password = str(self.password_box.stringValue())
        self.spotify.login(username, password)
        self.login_window.orderOut_(self)

    @IBAction
    def focusSearchWindow_(self, sender):
        if self.search_window.isKeyWindow():
            NSApp.hide_(None)
        else:
            NSApp.arrangeInFront_(None)
            self.search_window.makeKeyAndOrderFront_(None)
            NSApp.activateIgnoringOtherApps_(True)
            self.search_window.makeFirstResponder_(self.search_box)

    @IBAction
    def doQuery_(self, sender):
        def _browse_album_cb(loaded, not_loaded):
            def _display_cover_callback(loaded, not_loaded):
                self.result_table.reloadData()

            self.result = loaded[0].albums()
            self.result_names = []
            self.result_images = {}
            for a in self.result:
                self.result_names.append(a.name())
                self.result_images[a] = ImageProxy(a, _display_cover_callback)  # TODO: load image
            self.result_table.reloadData()

        if self.state == "track_browsing":
            self.switch_state()

        query = self.search_box.stringValue().encode("utf-8")
        if len(query) < 1:
            NSLog("no query string")
            return
        if self.last_query == query:
            NSLog("old query: %@", query)
            return
        self.last_query = query
        self.spotify.search_first_artists_albums(query, _browse_album_cb)

    @IBAction
    def exit_(self, sender):
        NSApp.terminate_(None)

    @IBAction
    def nextTrack_(self, sender):
        self.spotify.current_track_idx += 1
        self.spotify.play()

    @IBAction
    def previousTrack_(self, sender):
        self.spotify.current_track_idx -= 1
        self.spotify.play()

    @IBAction
    def togglePause_(self, sender):
        self.spotify.togglePause()

    def switch_state(self):
        if self.state == "album_browsing":
            self.state = "track_browsing"
            self.result_table.setRowHeight_(40.0)
            self.result_table.reloadData()
        else:
            self.state = "album_browsing"
            self.result_table.setRowHeight_(90.0)
            self.result_table.reloadData()

    def doubleClick(self):
        rowNumber = self.result_table.clickedRow()
        if self.state == "album_browsing":
            def loaded_album_tracks(loaded, not_loaded):
                self.selected_album_details = loaded[0]
                self.track_names = [t.name() for t in self.selected_album_details.tracks()]
                self.switch_state()

            self.selected_album = self.result[rowNumber]
            self.spotify.album_details(self.selected_album, loaded_album_tracks)
        else:
            # self.spotify.playlist = [t.spotifyURL() for t in self.selected_album_details.tracks()]
            self.spotify.playlist = self.selected_album_details.tracks()
            self.spotify.current_track_idx = rowNumber
            self.spotify.play()

    def _initTableView(self):
        self.result_table.setTarget_(self)
        sel = objc.selector(self.doubleClick, signature="v@:")
        self.result_table.setDoubleAction_(sel)
        col = self.result_table.tableColumns()[1]
        col.dataCell().setVerticalCentering_(True)

    def _initStatusBarItem(self):
        iconPath = resource_path("minispot", "png")
        self.statusMenuItemIcon = NSImage.alloc().\
            initWithContentsOfFile_(iconPath)
        self.statusItem = NSStatusBar.\
            systemStatusBar().statusItemWithLength_(20)
        self.statusItem.setMenu_(self.status_menu)
        self.statusItem.setTitle_("MiniSpot")
        self.statusItem.setImage_(self.statusMenuItemIcon)

    """ NSTableView delegate methods """
    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, rowIdx):
        if self.state == "album_browsing":
            a = self.result[rowIdx]
            if tableColumn.identifier() == "image_col":
                return self.result_images[a]()
            else:
                return self.result_names[rowIdx]
        else:
            if tableColumn.identifier() == "image_col":
                return self.result_images[self.selected_album]()
            else:
                return self.track_names[rowIdx]

    def numberOfRowsInTableView_(self, tableView):
        if self.state == "album_browsing":
            return len(self.result)
        else:
            return len(self.track_names)

    """ NSApplication delegate methds """
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")

    def applicationShouldTerminate_(self, notfification):
        return self.spotify.terminate()

    def observeValueForKeyPath_ofObject_change_context_(self, key_path, object, change, context):
        NSLog("KEY_PATH: %@", key_path)
        if key_path == "spotify.login_state":
            if self.spotify.login_state == "login_failed":
                self.display_login_window()
                NSApp.presentError_modalForWindow_delegate_didPresentSelector_contextInfo_(
                    self.spotify.login_error, self.login_window, None, None, None)
        elif key_path == "spotify.current_track":
            self.search_window.setTitle_(self.spotify.current_track.name())
