""" Define some application-wide properties.

TODO: move these to a config file.
"""

from datetime import datetime

PROJECT_TITLE = 'Unofficial UEFA Euro 2016 Bet Game'
ADMINS = [ 'admin' ]

# iterable list of group ids
GROUP_IDS = ('A', 'B', 'C', 'D', 'E', 'F') 

# the final's match id
FINAL_ID = 51

# deadline for final tips (the beginning of the quarter finals)
FINAL_DEADLINE = datetime(2016,6,30, 21,00)

# beginning of stage 2 (after the end of the group phase)
STAGE2_DEADLINE = datetime(2016,6,23,  1,00)
