//
//  Categories.m
//  MiniSpot
//
//  Created by Julian Eberius on 13.03.12.
//  Copyright 2012 __MyCompanyName__. All rights reserved.
//

#import "Categories.h"

@implementation NSTextFieldCell (MyCategories)
- (void)setVerticalCentering:(BOOL)centerVertical
{
    @try { _cFlags.vCentered = centerVertical ? 1 : 0; }
    @catch(...) { NSLog(@"*** unable to set vertical centering"); }
}
@end