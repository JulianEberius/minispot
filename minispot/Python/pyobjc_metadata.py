import objc

# the following arcane incantation is in fact necessary to convert python callables
# to Objective-C blocks via PyObjC
objc.registerMetaDataForSelector(b"SPAsyncLoading", b"waitUntilLoaded:timeout:then:", {
    "arguments": {
        2 + 2: {
            "type": "^@", "callable": {
                "arguments": {
                    0: {"type": "^v"},
                    2: {"type": "@"},
                    3: {"type": "@"}
                }
            }
        }
    }
})
objc.registerMetaDataForSelector(b"SPPlaybackManager", b"playTrack:callback:", {
    "arguments": {
        2 + 1: {
            "type": "^@", "callable": {
                "arguments": {
                    0: {"type": "^v"},
                    2: {"type": "@"},
                }
            }
        }
    }
})
objc.registerMetaDataForSelector(b"SPSession", b"trackForURL:callback:", {
    "arguments": {
        2 + 1: {
            "type": "^@", "callable": {
                "arguments": {
                    0: {"type": "^v"},
                    2: {"type": "@"},
                }
            }
        }
    }
})
