import csv
import numpy as np
import statsmodels.api as sm
import os
from biosppy.signals import *
import sys


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


def find_PPG_peaks_old(vec):
    mids = find_ECG_peaks(vec)
    mids = [i[0] for i in mids]
    #print(mids, file=sys.stderr)
    ret = []
    up = []

    MAGIC = 50

    for i in mids:
        mx, mn = i, i
        for j in range(i, min(i + MAGIC, len(vec))):
            if vec[j] > vec[mx]:
                mx = j
        for j in range(max(i - MAGIC, 0), i):
            if vec[j] < vec[mn]:
                mn = j
        ret.append([mn, vec[mn]])
        ret.append([mx, vec[mx]])
        up.append([mx, vec[mx]])
    return ret, up

"""
def find_PPG_peaks(vec):
    av = find_diff(find_ECG_peaks(vec))
    tr, tru = find_PPG_peaks_old(vec)
    ret = []
    up = []

    for i in range(min(3, len(tr))):
        ch = [tr[0]]
        for j in range(len(tr)):
            if av / (tr[j][0] - ret[len(ret) - 1][0]) > 1.5

        vec = vec[1:]

    return ret, up
"""


def parse(file):
    cur = reader(file)

    # return [cur[0], cur[1], cur[2][0], cur[3][0]]

    SBP = cur[0]
    DBP = cur[1]
    PPG = cur[2]
    ECG = cur[3]

    # find peaks
    try:
        temp = find_PPG_peaks_old(PPG)
        PPG_peaks = temp[0]
        PPG_peaks_up = temp[1]
    except:
        print(file.name + ' PPG', file=sys.stderr)
        PPG_peaks = [[0, 0]]
        PPG_peaks_up = [[0, 0]]

    try:
        ECG_peaks = find_ECG_peaks(ECG)
    except:
        print(file.name + ' ECG', file=sys.stderr)
        ECG_peaks = [[0, 0]]

    #print(ECG_peaks, PPG_peaks, PPG_peaks_up, file=sys.stderr)

    # find average diff in ppg
    PPG_diff = find_diff([i[1] for i in PPG_peaks])

    # find average delay
    merge = []
    p1, p2 = 0, 0
    while p1 < len(PPG_peaks_up) and p2 < len(ECG_peaks):
        while p1 < len(PPG_peaks_up) and PPG_peaks_up[p1][0] < ECG_peaks[p2][0]:
            p1 += 1
        if p1 == len(PPG_peaks_up):
            break
        while p2 < len(ECG_peaks) - 1 and PPG_peaks_up[p1][0] > ECG_peaks[p2 + 1][0]:
            p2 += 1
        if p2 == len(ECG_peaks):
            break
        if p1 < len(PPG_peaks_up) and p2 < len(ECG_peaks):
            merge.append(ECG_peaks[p2])
            p2 += 1
            merge.append(PPG_peaks_up[p1])
            p1 += 1
    merge_diff = find_diff([merge[i][0] for i in range(len(merge))])

    if merge_diff > 400:
        DEBUG = 1

    # ret
    return [SBP, DBP, PPG_diff, merge_diff]
    #return [SBP, DBP, PPG_diff]


if __name__ == '__main__':
    dir = input()
    files = os.listdir(dir)
    all = {}
    data = {}

    SBPs = {}
    DBPs = {}

    for file in files:
        person = file[file.find('subj') + 4:file.find('log')]
        if person not in data:
            data[person] = []


        if file == 'subj11log693.csv':
            DEBUG = 1

        add = parse(open(dir + '/' + file, 'r'))

        #add = add[:len(add) - 1]

        if add[0] != 0 or add[1] != 0:
            data[person].append(add)
        all[file] = add

    for person in data:
        leng = len(data[person][0])
        cur = [[data[person][j][i] for j in range(len(data[person]))] for i in range(leng)]

        SBP = cur[0]
        DBP = cur[1]
        cur = cur[2:]

        num = len(cur)

        cur = np.array(cur).T
        #cur = sm.add_constant(cur)
        SBP_results = sm.OLS(endog=SBP, exog=cur).fit()
        DBP_results = sm.OLS(endog=DBP, exog=cur).fit()

        SBP_out = str(SBP_results.summary())
        SBPs[person] = []
        for i in range(1, num + 1):
            name = 'x' + str(i)
            res = SBP_out[SBP_out.find(name):SBP_out.find(name) + 21]
            res = float(res[len(res) - 6:])
            SBPs[person].append(res)

            """
            print(person, file=sys.stderr)
            print(name, end=': ', file=sys.stderr)
            print(res, file=sys.stderr)
            """

        DBP_out = str(DBP_results.summary())
        DBPs[person] = []
        for i in range(1, num + 1):
            name = 'x' + str(i)
            res = DBP_out[DBP_out.find(name):DBP_out.find(name) + 21]
            res = float(res[len(res) - 6:])
            DBPs[person].append(res)

    with open('coeffs.csv', mode='w') as to:
        for person in data:
            print(person, file=to)
            print('SBP: ', end='', file=to)
            for i in SBPs[person]:
                print(i, end=' ', file=to)
            print('', file=to)
            print('DBP: ', end='', file=to)
            for i in DBPs[person]:
                print(i, end=' ', file=to)
            print('', file=to)

    with open('ans.csv', mode='w') as to:
        for file in files:
            person = file[file.find('subj') + 4:file.find('log')]
            array = all[file]
            array = array[2:]
            #array = array[::-1]
            SBP = 0
            DBP = 0
            for i in range(len(array)):
                SBP += SBPs[person][i] * array[i]
                DBP += DBPs[person][i] * array[i]
            print(file + ',' + str(int(round(SBP))) + ',' + str(int(round(DBP))), file=to)