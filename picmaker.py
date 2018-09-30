import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import hilbert, chirp
from biosppy import storage
from biosppy.signals import *

number_of_rows = 15000

#file = input()
file = 'data_train/subj11log693.csv'

df = pd.read_csv(file, header=None, names=['PPG', 'ECG'], usecols=['PPG','ECG'], skiprows=1, nrows=number_of_rows)

df.plot(y='PPG', color='g')
df.plot(y='ECG', color='r')
plt.show()


signal = df.get('ECG')
out = ecg.ecg(signal=signal, sampling_rate=500.0, show=True)
out[2]

