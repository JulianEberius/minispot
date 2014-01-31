#-*- coding: utf-8 -*-
#
#  spotify.py
#  minispot
#
#  Created by Julian Eberius on 28.01.14.
#  Copyright (c) 2014 Julian Eberius. All rights reserved.
#

import objc
import pyobjc_metadata
from Foundation import NSClassFromString, NSLog, NSUserDefaults

PySpotify = NSClassFromString("PySpotify")
SPSession = NSClassFromString("SPSession")
SPSearch = NSClassFromString("SPSearch")
SPAsyncLoading = NSClassFromString("SPAsyncLoading")
SPArtistBrowse = NSClassFromString("SPArtistBrowse")
SPAlbumBrowse = NSClassFromString("SPAlbumBrowse")
SPSessionPlaybackDelegate = objc.protocolNamed("SPSessionPlaybackDelegate")


def async_load(items, callback):
    SPAsyncLoading.waitUntilLoaded_timeout_then_(items, 20.0, callback)


class Spotify(PySpotify, SPSessionPlaybackDelegate):

    playlist = []  # list of SPTrack
    login_state = "logged_out"
    login_error = None
    current_track = None

    _current_track_idx = -1

    @property
    def current_track_idx(self):
        return self._current_track_idx

    @current_track_idx.setter
    def current_track_idx(self, value):
        self._current_track_idx = value
        self.current_track = self.playlist[self._current_track_idx]

    def init(self):
        self = super(Spotify, self).init()
        SPSession.sharedSession().setPlaybackDelegate_(self)

        return self

    def play(self):
        def _error_cb(error):
            if error:
                NSLog("Error playing track: %@", error)

        def _play_cb(loaded, not_loaded):
            self.playbackManager().playTrack_callback_(loaded[0], _error_cb)

        def _track_cb(track):
            if track is not None:
                async_load(track, _play_cb)

        url = self.current_track.spotifyURL()
        if url:
            SPSession.sharedSession().trackForURL_callback_(url, _track_cb)
        else:
            NSLog("Nothing to play.")

    def togglePause(self):
        self.playbackManager().setIsPlaying_(not self.playbackManager().isPlaying())

    def sessionDidLosePlayToken_(self, session):
        NSLog("Lost Token!")

    def sessionDidEndPlayback_(self, session):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "sessionDidEndPlaybackOnMainThread:", session, False)

    def sessionDidEndPlaybackOnMainThread_(self, session):
        self.current_track_idx += 1
        if self.current_track_idx < len(self.playlist):
            self.play()
        else:
            self.current_track_idx = -1

    def session_didGenerateLoginCredentials_forUserName_(self, session, credentials, username):
        NSLog("storing credentials: %@", credentials)
        defaults = NSUserDefaults.standardUserDefaults()
        storedCredentials = defaults.valueForKey_("SpotifyUsers")

        if storedCredentials is None:
            storedCredentials = {}
        else:
            storedCredentials = storedCredentials.mutableCopy()

        storedCredentials[username] = credentials
        storedCredentials["DEFAULT_USER"] = username
        defaults.setValue_forKey_(storedCredentials, "SpotifyUsers")

    def login(self, username, password):
        SPSession.sharedSession().attemptLoginWithUserName_password_(username, password)

    def login_saved_credentials(self):
        defaults = NSUserDefaults.standardUserDefaults()
        storedCredentials = defaults.valueForKey_("SpotifyUsers")

        if not storedCredentials:
            return False

        if not "DEFAULT_USER" in storedCredentials:
            return False

        username = storedCredentials["DEFAULT_USER"]
        credentials = storedCredentials[username]
        if not credentials:
            return False

        SPSession.sharedSession().attemptLoginWithUserName_existingCredential_(username, credentials)
        return True

    def sessionDidLoginSuccessfully_(self, session):
        NSLog("Login succesfull")
        self.login_state = "logged_in"

    def session_didFailToLoginWithError_(self, session, error):
        NSLog("Login error: %@", error)
        self.login_error = error
        self.login_state = "login_failed"

    def sessionDidLogOut_(self, session):
        self.login_state = "logged_out"

    def search_first_artists_albums(self, query, callback):
        session = SPSession.sharedSession()
        result = SPSearch.searchWithSearchQuery_inSession_(query, session)

        def _browse_artist(loaded, not_loaded):
            if len(loaded[0].artists()) > 0:
                result = SPArtistBrowse.browseArtist_inSession_type_(loaded[0].artists()[0], session, 1)
                async_load(result, callback)
            else:
                NSLog("Not found %@", query)
        async_load(result, _browse_artist)

    def album_details(self, album, callback):
        session = SPSession.sharedSession()
        result = SPAlbumBrowse.browseAlbum_inSession_(album, session)
        async_load(result, callback)
