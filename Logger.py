# log info to syslog

import Foundation
def log(s):
    Foundation.NSLog( "%s: %s" % ("PyeTV", str(s) ) )
    pass

