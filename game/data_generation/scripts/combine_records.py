"""
This script is used to combine the misc. training data created by the multiple threads
running Data_Collector instances.

Data Source:  $(PROJECT_ROOT)/game/data_generation/records/*.p
Combo Output: $(PROJECT_ROOT)/game/data_generation/records.p

Gunnar Horve <gunnarhorve@gmail.com>
Last Update: 04/30/2018
"""

import definitions as d
import os
import pickle

combined_records = []

for file in os.listdir(d.DATA_POOLING_DIR):
    if file.endswith(".p"):
        file_path = os.path.join(d.DATA_POOLING_DIR, file)
        record = pickle.load(open(file_path, "rb"))
        combined_records += record

pickle.dump(combined_records, open(d.TRAINING_DATA, "wb"))
