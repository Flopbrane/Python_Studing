#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# Author: F.Kurokawa
# Description:
# Load CSV file method
#########################

import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from pandas import DataFrame
from dateutil.parser import parse
import string
# ☆入力ファイル選択ダイアログをGUIで表示し、CSVファイル名を選択するクラス
class FileSelector: #file_path(str)を返す
    def __init__(self, root):
        self.root = root

    def select_file(self, filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))):
        print("Execute select_file Method")
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        self.file_path = file_path
        if not file_path:
            messagebox.showerror("WM_DELETE_WINDOW","ファイル名が存在しません")
            sys.exit(1)
        return file_path
    
# 指定されたファイルの読み込み、列数確認、列ヘッダー対処
class CSVFileReader: #DataFrameを返す。
    def __init__(self, file_path, start_col=None, fixed_width=False):
        self.file_path = file_path
        self.start_col = start_col
        self.fixed_width = fixed_width
        self.data = None # ここで self.data を初期化
        self.data = self.check_for_column() # ここで列のチェックを行う

        # 列数の確認
    def check_for_column(self):
        # 列ヘッダーがあるかどうかを判断
        # ファイルを開いて、1行目だけ読み込む
        with open(self.file_path, 'r') as f: 
            first_line = f.readline().strip()
        # 列ヘッダーの有無と対処をしてself.dataに読み込む
        self.has_header = self.check_for_header(first_line)
        self.data =self.read_and_set_columuns()
        return self.data

    def read_and_set_columuns(self) -> DataFrame:
        has_header = self.has_header
        # 固定幅のファイルの読み込み（固定幅長は逐次変更が必要）
        if self.fixed_width:
            widths = [19, 6, 7, 6, 7, 6, 7, 6, 5, 4, 5, 20, 5]  # 各カラムの幅を指定
            names = ["Origin Time", "OTerr", "Lat", "LatErr", "Long", "LonErr", "Dep", "DepErr", "Mag", "Region", "Flag"]
            self.data = pd.read_fwf(self.file_path, widths=widths, names=names, skiprows=4)  # skiprows(行飛ばし)でヘッダー部分をスキップ
        else:
            # 既存のconmma_separate_valueの読み込み処理  
            if has_header:
                self.data = pd.read_csv(self.file_path)  # 仮に10000列までとしています ←, usecols=range(self.start_col, 10000)を追加
            else:
                self.data = pd.read_csv(self.file_path, header=None) # ←, usecols=range(self.start_col, 10000)
                # カラム数によって列名を設定
                n_cols = self.data.shape[1] # ここで n_cols を設定
                if n_cols == 6:
                    self.data.columns = pd.Index(['DATETIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'TICK'])
                elif n_cols == 7:
                    self.data.columns = pd.Index(['DATE', 'TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'TICK'])
                else:
                    # 最初の列を'DATETIME'として、残りの列にはアルファベットを割り当てます。
                    alphabet = list(string.ascii_uppercase)
                    self.data.columns = pd.Index(['DATETIME'] + alphabet[:n_cols-1])
        return self.data

        # 列ヘッダーがあるかどうかをチェック
    def check_for_header(self,first_line: str):
        try:
            # 1列目だけ取り出す
            first_column_value = first_line.split(',')[0]
            # DATEtime型に変換を試みる
            parse(first_column_value)
            return False   #エラーが発生しなければ、これはヘッダーではない
        except ValueError:
            return True   #エラーが発生すれば、これはヘッダー
        
        
#########################
# ★メインプログラム
#########################
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    # ファイル選択ダイアログを表示
    file_selector = FileSelector(root)
    file_path = file_selector.select_file()
    # CSVファイルの読み込み
    csv_reader = CSVFileReader(file_path)
    data = csv_reader.data
    print(data)
    print(data.columns)
    print(data.shape)
    print(data.dtypes)
    print(data.describe())
    print(data.head())
    print(data.tail())
    print(data.info())
    print(data.isnull().sum())
    print(data.isnull().sum().sum())
    print(data.isnull().any())
    print(data.isnull().any().any())
    print(data.isnull().values.sum())
    print(data.isnull().values.any())
    print(data.isnull().values.any().any())
    print(data.isnull().values.sum().sum())
    print(data.isnull().sum(axis=0))
    print(data.isnull().sum(axis=1))
    print(data.isnull().sum(axis=0).sum())
    print(data.isnull().sum(axis=1).sum())
    print(data.isnull().sum(axis=0).any())
    print(data.isnull().sum(axis=1).any())
    print(data.isnull().sum(axis=0).any().any())
    print(data.isnull().sum(axis=1).any().any())
    print(data.isnull().sum(axis=0).values.sum())
    print(data.isnull().sum(axis=1).values.sum())
    print(data.isnull().sum(axis=0).values.any())
    print(data.isnull().sum(axis=1).values.any())
    print(data.isnull().sum(axis=0).values.any().any())
    print(data.isnull().sum(axis=1).values.any().any())
    print(data.isnull().sum(axis=0).values.sum().sum())
    print(data.isnull().sum(axis=1).values.sum().sum())
    print(data.isnull().sum(axis=0).values.any().any().any())
    print(data.isnull().sum(axis=1).values.any().any().any())
    print(data.isnull().sum(axis=0).values.sum().sum().sum())
    print(data.isnull().sum(axis=1).values.sum().sum().sum())
    print(data.isnull().sum(axis=0).values.any().any().any().any())
