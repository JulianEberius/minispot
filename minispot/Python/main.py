#-*- coding: utf-8 -*-
#
#  main.py
#  minispot
#
#  Created by Julian Eberius on 28.01.14.
#  Copyright Julian Eberius 2014. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

objc.setVerbose(1)

# import modules containing classes required to start application and load MainMenu.nib
import AppDelegate

# pass control to AppKit
AppHelper.runEventLoop()
