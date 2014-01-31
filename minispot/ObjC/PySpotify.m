//
//  SimplePlayerAppDelegate.m
//  SimplePlayer
//
//  Created by Daniel Kennett on 04/05/2011.
/*
 Copyright (c) 2011, Spotify AB
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
 notice, this list of conditions and the following disclaimer in the
 documentation and/or other materials provided with the distribution.
 * Neither the name of Spotify AB nor the names of its contributors may
 be used to endorse or promote products derived from this software
 without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL SPOTIFY AB BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#import "PySpotify.h"
#include "../appkey.c"

@implementation PySpotify

@synthesize playbackManager;

-(id)init {
	NSError *error = nil;
	[SPSession initializeSharedSessionWithApplicationKey:[NSData dataWithBytes:&g_appkey length:g_appkey_size]
											   userAgent:@"com.github.julianeberius.minispot"
										   loadingPolicy:SPAsyncLoadingManual
												   error:&error];
	if (error != nil) {
		NSLog(@"CocoaLibSpotify init failed: %@", error);
		abort();
	}

	[[SPSession sharedSession] setDelegate:self];
	self.playbackManager = [[SPPlaybackManager alloc] initWithPlaybackSession:[SPSession sharedSession]];
    return self;
}


- (NSApplicationTerminateReply)terminate {
	if ([SPSession sharedSession].connectionState == SP_CONNECTION_STATE_LOGGED_OUT ||
		[SPSession sharedSession].connectionState == SP_CONNECTION_STATE_UNDEFINED)
		return NSTerminateNow;

	[[SPSession sharedSession] logout:^{
		NSLog(@"Logged out succesfully");
		[[NSApplication sharedApplication] replyToApplicationShouldTerminate:YES];
	}];
	return NSTerminateLater;
}

@end
