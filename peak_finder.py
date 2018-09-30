import csv
import numpy as np
import statsmodels.api as sm
import os
from biosppy.signals import *
import sys
os.environ['OCTAVE_EXECUTABLE'] = 'C:\Octave\Octave-4.4.1\'
from oct2py import octave


def reader(file):
    rd = csv.reader(file)
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


def find_ECG_peaks(vec):
    # return vec

    out = ecg.ecg(signal=np.array(vec), sampling_rate=500.0, show=False)
    return [[i, vec[i]] for i in out[2]]


def find_PPG_peaks(vec):
    cur = np.array(vec)
    octave.eval("pkg load signal")
    peaks, indexes = octave.findpeaks(cur, 'DoubleSided', 'MinPeakHeight', 1000, 'MinPeakDistance', 50, 'MinPeakWidth', 0)
    return indexes


def parse(file):
    cur = reader(file)

    # return [cur[0], cur[1], cur[2][0], cur[3][0]]

    SBP = cur[0]
    DBP = cur[1]
    PPG = cur[2]
    ECG = cur[3]

    # find peaks
    try:
        temp = find_PPG_peaks(PPG)
        PPG_peaks = temp[0]
        PPG_peaks_up = temp[1]
    except:
        print(file.name + ' PPG', file=sys.stderr)
        PPG_peaks = [[0, 0]]
        PPG_peaks_up = [[0, 0]]

    return PPG_peaks_up


if __name__ == '__main__':
    file = 'data_train/subj11log693.csv'
    print(func_peaks(open(file)))
