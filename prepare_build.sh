#!/bin/sh
git submodule init
git submodule update
pushd Libraries/cocoalibspotify/scripts
./update-libspotify-version.py 12.1.45 12.1.51
popd