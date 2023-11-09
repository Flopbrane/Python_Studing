#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# Author: F.Kurokawa
# Description:
# 固定長の数値データを読み込むプログラム
#########################

import sys
import pandas as pd
import tkinter as tk
from tkinter import Tk, Label, Entry, Button,filedialog, messagebox
from dateutil.parser import parse
import re
import string
from collections import Counter
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
            sys.exit()
        return file_path

class DataProcessor: # データ処理クラス
    
    def __init__(self, file_path):
        self.file_path = file_path # ファイルパス
        
        self.data_header_list = [] # ヘッダーリスト
        self.col_specs = [] # 数値データの各列の文字数をリスト化したもの
        
        self.all_line_number = 0 # ファイルの全行数
        self.data_start_line_number = 0 # 数値データの開始行の行番号
        self.last_line_number = 0 # ファイルの最終行の行番号
        
        self.header_count = 0 # ヘッダー項目数
        self.num_column_count = 0 # 数値データの列数
        
        self.data_holder = "" # 行データを一時的に保持する
        self.header_line = "" # ヘッダーデータ行
        
        self.df: pd.DataFrame  # データフレーム
        
        
    def analyze_data(self): # 全体の統合処理
        # ★条件出しの処理
        # ファイルの最終行の行番号を取得
        try:
            file_path = self.file_path
            self.last_line_number = self.count_lines(file_path) 
        except ValueError as e: # ファイルが空の場合のエラー処理
            messagebox.showerror("error", str(e))
            sys.exit(1)
        print(f"ファイルの最終行の行番号: {self.last_line_number}")
        # 数値データ行を探す処理
        try:
            self.find_numerical_data_row() 
        except ValueError as e: # 数値データ行が見つからない場合のエラー処理
            messagebox.showerror("error", str(e))
            sys.exit(1)
        print(f"数値データの開始行番号: {self.data_start_line_number}")
        print(f"ヘッダーリスト: {self.data_header_list[:]}")
        # 数値データ行から列数を取得し、列の文字数をリスト化する処理
        self.parse_data_line() 
        # ★データの読み込み処理
        # データ読み込み処理
        self.df = self.data_reader(self.file_path)         
        # 数値データ列数とヘッダー項目数が合致しない場合,列名を入力してもらう処理(ヘッダー無しと推測)
        if self.compare_header_and_data() is False: 
            self.prompt_for_header(root) # 列名を入力してもらう処理
            self.df = self.add_column_names(self.df, self.data_header_list) # 列名をデータフレームに追
            return self.df # データフレームを返す
        # 数値データ行が最初の行の場合(ヘッダー無しと推測)
        if self.data_start_line_number == 0:
            self.data_reader(self.file_path) # データ読み込み処理 
            self.prompt_for_header(root)
            self.df = self.add_column_names(self.df, self.data_header_list) # 列名をデータフレームに追加
            return self.df # データフレームを返す
        # 数値データ行が最初の行以外の場合(ヘッダー有りと推測)
        elif self.data_start_line_number > 0: 
            self.df = self.add_column_names(self.df, self.data_header_list) # 列名をデータフレームに追加
            return self.df # データフレームを返す

        else:
            self.assign_default_headers() # 列名不明の場合、アルファベット順に列ヘッダーを付ける処理
            self.df = self.add_column_names(self.df, self.data_header_list) # 列名をデータフレームに追加            
            return self.df # データフレームを返す
        
    def data_reader(self, file_path): # データ読み込み処理
        self.file_path = file_path # ファイルパスを取得
        self.df = pd.read_fwf(self.file_path, colspecs=self.col_specs, header=None, skiprows=self.data_start_line_number) # データフレームを作成
        self.df = self.df.dropna(how='all')  # 全ての列がNaNの行を削除する
        return self.df # データフレームを返す

    
    def find_numerical_data_row(self): # 数値データ行を探す処理
        """
        --------Args-------
        self.file_path: str # ファイルパス
        self.data_holder: str # 前に読み込み保持していた行（ヘッダー行）
        self.data_header_list: list # ヘッダー行をリスト化したもの
        self.numerical_line: str # 数値データ行
        self.data_start_line_number: int # データの開始行の行番号
        """
        self.data_holder = "" # 行データを一時的に保持する
        file_path = self.file_path # ファイルパスを取得
        with open(file_path, 'r', encoding='utf-8') as file: # ファイルをUTF-8エンコーディングで開く
            for i, line in enumerate(file): # ファイルを1行ずつ読み込みながら行番号(i)を取得
                self.header_line = self.data_holder # 前に読み込んだ行をヘッダーデータ行として保持する               
                self.data_holder = line # 現在の行を一時的に保持する
                if self.contains_number(): # 現在の行に数値が含まれているとき、Tureを返す → 数値データ行と判定
                    self.data_start_line_number = i # データの開始行の行番号を設定
                    self.parse_header() # 直前に保持していた行（ヘッダー行）をリスト化して保存 self.data_header_list
                    self.flag = True # 
                    break # ループを抜ける
                elif i == self.last_line_number:
                    raise ValueError("数値データ行が見つかりませんでした")
                else:
                    continue

        return self.data_start_line_number, self.data_header_list, self.data_holder # 数値データ行の行番号とヘッダーリスト、数値行を返す
    
    def parse_data_line(self): # 数値データ行から列数を取得し、列の文字数をリスト化する処理
        list_of_column_widths = []
        line_str = self.data_holder
        col_start = 0
            # 文字が見つかるまでスキップ
        while col_start < len(line_str) and line_str[col_start].isspace(): # isspace()は空白文字かどうかを判定するメソッド
            col_start += 1
        # 行の末尾まで処理
        while col_start < len(line_str):
            col_end = col_start
            # 非空白文字を探し、列の終わりまで進む
            while col_end < len(line_str) and not line_str[col_end].isspace():
                col_end += 1
            # 現在の列の始点と終点をリストに追加
            list_of_column_widths.append((col_start, col_end))
            # 次の列の始点を探し、スペースをスキップ
            col_start = col_end
            while col_start < len(line_str) and line_str[col_start].isspace():
                col_start += 1
        return list_of_column_widths  # 列の幅をリスト化したものを返す
    
    def check_for_header(self): # 最初の行から1列目を取り出し、日付としてパースできるかどうかをチェックする処理
        first_column_value = self.data_header_list[0]
        try:
            # 日付としてパースを試みる
            parse(first_column_value)
            # パースに成功した場合、これはデータ行である
            return False
        except ValueError:
            # パースに失敗した場合、これはヘッダー行である
            return True
        
    def compare_header_and_data(self): # 数値データ列数とヘッダー項目数が合致するかをチェックする処理
        self.num_column_count = len(self.col_specs) # 数値データ列数を取得
        header_count = len(self.data_header_list) # ヘッダー項目数を取得
        if self.num_column_count == header_count:
            return True # 数値データ列数とヘッダー項目数が合致する場合、Trueを返す
        else:
            return False # 数値データ列数とヘッダー項目数が合致しない場合、Falseを返す
    
    def prompt_for_header(self,root): # GUIを立ちあげて、列名入力を促す処理
        root = tk.Tk()
        root.title('列名を入力してください')
        root.geometry('250x300')
        num_columns = len(self.col_specs)
        entries = []
        self.columns_names_list = []
        for i in range(num_columns):
            Label(root, text=f'列{i+1}の名前:').grid(row=i, column=0)
            entry = Entry(root)
            entry.grid(row=i, column=1)
            entries.append(entry)

        def on_submit(): # 決定ボタンが押されたら、列名を取得する
            self.columns_names_list = [entry.get() for entry in entries]
            root.destroy()
            return self.columns_names_list

        submit_btn = Button(root, text='決定', command=on_submit)
        submit_btn.grid(row=num_columns, column=1)
        root.mainloop()
        return self.columns_names_list # 列ヘッダー名を返す
    
   
    def add_column_names(self, df, column_names:list ): # 列名をデータフレームに追加
        df = self.df
        df.columns = column_names
        self.df = df
        return self.df
    
    def assign_default_headers(self): # 列名不明の場合、アルファベット順に列ヘッダーを付ける処理
        # 最初の列を'DATETIME'として、残りの列にはアルファベットを割り当てます。
        self.df: pd.DataFrame
        n_cols = self.num_column_count
        alphabet = list(string.ascii_uppercase)
        self.df.columns = ['DATETIME'] + alphabet[:n_cols-1]
        return self.df

   
    def contains_number(self)-> bool: # 数値が含まれている行をチェックする関数
        if "█" in self.header_line: # "█"が含まれていたらFalseを返す
            return False
        return bool(re.search(r'\d', self.header_line)) # 数値が含まれていたらTrueを返す(数値じゃなかったらFalseを返す)

    def parse_header(self): # 一番多い文字を区切り文字として、ヘッダー名をリスト化する処理
        # collections.Counterを使用して各文字の出現回数を数えます。
        if self.header_line == "":
            self.data_header_list = []
            return self.data_header_list
        counter = Counter(self.header_line)
        # 最も多い文字（区切り文字）を取得します。
        delimiter = counter.most_common(1)[0][0]
        # その文字を無視して残りの部分からヘッダー名をリスト化します。
        # ここでは、split()メソッドを使用して行を分割します。
        self.data_header_list = [header for header in self.header_line.split(delimiter) if header]

    def count_lines(self, file_path: str) -> int: # ファイルの行数をカウントする処理
        with open(file_path, 'r', encoding='utf-8') as file:
            self.all_line_number = sum(1 for line in file)
            if self.all_line_number == 0:
                raise ValueError("ファイルが空です")
            return self.all_line_number
############################
# ★メインプログラム
############################
if __name__ == '__main__':
    
    root = tk.Tk() # tkウインド(メインウインド)を表示
    root.withdraw() # tkウインドを隠す
    
    file_selector = FileSelector(root)
    file_path = file_selector.select_file()
    print(file_path)
    
    processor = DataProcessor(file_path)
    processor.analyze_data()
    print(processor.df.head())
