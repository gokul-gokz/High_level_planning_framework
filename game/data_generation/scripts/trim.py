"""
This script is (hopefully) an anachronism.  Its original intent was to remove malformed data points
from the records.p file.  Data collection has since been updated, so we have very few (No?) malformed
data points.

Gunnar Horve <gunnarhorve@gmail.com>
Last Update: 04/30/2018
"""

import pickle
import definitions as d

data = pickle.load(open(d.TRAINING_DATA, "rb"))

bad_data_tuple = (234, 208, 0, 100, -1, -1, False, 400.0, 272.0)

print "length before deletion: " + len(data)
for i in data:
    if i[0] == bad_data_tuple and i[3] == bad_data_tuple:
        print i, data.index(i)
        data.remove(i)
        break
print "length after delection: " + len(data)

pickle.dump(data, open(d.TRAINING_DATA, "wb"))
