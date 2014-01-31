all:
	xcodebuild install -scheme minispot -workspace minispot.xcworkspace

debug:
	xcodebuild -scheme minispot -workspace minispot.xcworkspace

install:
	xcodebuild install -scheme minispot -workspace minispot.xcworkspace


