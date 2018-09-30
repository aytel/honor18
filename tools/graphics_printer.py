import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import hilbert, chirp
from biosppy import storage
from biosppy.signals import *
import sys
import os
import imp

number_of_rows = 15000

#file = input()
# file = 'data_train/subj11log693.csv'
file = sys.argv[1]

df = pd.read_csv(file, header=None, names=['PPG', 'ECG'], usecols=['PPG','ECG'], skiprows=1, nrows=number_of_rows)

print(df)

df.plot(y='PPG', color='g')
df.plot(y='ECG', color='r')
plt.show()
