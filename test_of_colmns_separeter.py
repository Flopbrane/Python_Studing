#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# Author: F.Kurokawa
# Description:
# 固定長データの列推測(ヘッダーなし, 数値データのみ)
#########################

import pandas as pd
import numpy as np
import re as re
import sys

# ヘッダーのリスト
header_list = [
    "Origin Time", "OTerr", "Lat", "LatErr", "Long", "LonErr", "Dep", "DepErr", 
    "Mag", "Region", "Flag"
]

# sampleの数値データ
sample_data = [
    "2010-10-08 00:15:36.64  0.18   37.915  0.49  139.133  0.63    17.5   1.7  0.6V        NE NIIGATA PREF  K",
    "2010-10-08 00:15:37.09  0.05   34.608  0.13  132.355  0.10    21.6   0.4  0.0V        WESTERN HIROSHIMA PREF  K",
    "2010-10-08 00:17:42.91  0.21   35.062  0.66  139.929  0.85    58.6   1.8  1.3V        SOUTHERN BOSO PENINSULA  K",
    "2010-10-08 00:20:14.28  0.03   34.959  0.11  135.451  0.11    10.1   0.4  0.3V        KYOTO OSAKA BORDER REG  K",
    "2010-10-08 00:25:00.99  0.13   36.913  0.63  140.798  0.93    85.9   1.0  0.6V        EASTERN FUKUSHIMA PREF  K",
    "2010-10-08 00:25:01.38  0.11   37.282  0.31  139.999  0.19     8.9   1.6  0.3V        WESTERN FUKUSHIMA PREF  K",
    "2010-10-08 00:27:20.68  0.35   24.731  2.59  124.282  1.77    59.6   3.0  0.6v        NEAR ISHIGAKIJIMA ISLAND  K",
    "2010-10-08 00:39:05.27  0.37   37.866  0.82  139.222  1.08   158.0   3.2  1.4V        NE NIIGATA PREF  K",
    "2010-10-08 00:40:53.31  0.19   37.741  1.22  142.228  1.40    33.8   2.7  1.0v        SE OFF MIYAGI PREF  K",
    "2010-10-08 00:47:02.72  0.06   34.284  0.18  139.212  0.31     9.5   0.6  2.3V        NEAR NIIJIMA ISLAND  K"
]



# 2つ以上のスペースで文字列を分割する関数
def split_by_spaces(line):
    return re.split(r'\s{2,}', line)

# 各行を分割してリストに格納
split_lines = [split_by_spaces(line) for line in sample_data]

# データフレームを作成
df_earthquake = pd.DataFrame(split_lines, columns=header_list)

print(split_lines[0])
print(df_earthquake)
