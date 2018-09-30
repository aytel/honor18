import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import hilbert, chirp
from biosppy import storage
from biosppy.signals import *
import sys
import os
import math
from oct2py import octave
import csv
import statsmodels.api as sm

# return [SBP, DBP, PPG, ECG]
def reader(file_object):
    rd = csv.reader(file_object)
    PPG = []
    ECG = []
    fr = True
    SBP, DBP = 0, 0
    for row in rd:
        if fr:
            SBP = int(row[0])
            DBP = int(row[1])
            fr = False
        else:
            PPG.append(int(row[0]))
            ECG.append(int(row[1]))
    return [SBP, DBP, PPG, ECG]


def find_ECG_peaks(vec):
    # return vec
    out = ecg.ecg(signal=np.array(vec), sampling_rate=500.0, show=False)
    return out[2]


def find_diff(peaks):
    count = 0
    summ = 0
    if len(peaks) > 1 and peaks[1] < peaks[0]:
        peaks = peaks[1:]
    for i in range(len(peaks)):
        if i % 2 == 0:
            continue
        count += 1
        summ += abs(peaks[i] - peaks[i - 1])
    if count == 0:
        return 0
    return summ / count


def find_PPG_peaks(vec):
    cur = np.array(vec)
    octave.eval("pkg load signal")
    res = octave.findpeaks(cur, 'DoubleSided', 'MinPeakHeight', 1000, 'MinPeakDistance', 50, 'MinPeakWidth', 0)
    print(res)
    # peaks, indexes = octave.findpeaks(cur)
    # return indexes


if __name__ == '__main__':
    filename = sys.argv[1]
    file_object = open(filename)

    SBP, DBP, PPG, ECG = reader(file_object)

    peaks = find_PPG_peaks(PPG)

    plt.title('PPG')
    plt.plot(PPG)

    xx = [0] * len(PPG)

    # for x in peaks:
        # xx[x] = PPG[x]

    plt.plot(xx, color = 'red')
    plt.show()

