#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# Author: F.Kurokawa
# Description:
# 固定長のデータを読み込む_書き換え
#########################

import sys
import pandas as pd
import tkinter as tk
from tkinter import Label, Entry, Button,filedialog, messagebox
from dateutil.parser import parse
import re
import string
from collections import Counter
from typing import Optional, List
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
    """
    固定長データの列数とヘッダー項目を分析し、データフレームに変換するクラス
    ★condition_flag: int
    0: 初期値
    1: 数値データ行が最初の行の場合(ヘッダー無しと推測, 各列名を入力)
    2: 数値データ行が最初の行以外の場合(ヘッダー有りと推測)
    3: 数値データ行が最初の行以外の場合(ヘッダー無しと推測)
    4: 数値データ行が最初の行以外の場合(ヘッダー無し, 各列にアルファベットを割り当てる)
    """
    def __init__(self, file_path):
        self.file_path = file_path # ファイルパス
        self.destruction_line = [] # 破棄予定行リスト
        self.data_header_list = [] # ヘッダーリスト
        self.col_specs = [] # 数値データの各列の文字数をリスト化したもの
        
        self.all_line_number = 0 # ファイルの全行数
        self.data_start_line_number = 0 # 数値データの開始行の行番号
        self.last_line_number = 0 # ファイルの最終行の行番号
        
        self.header_count = 0 # ヘッダー項目数
        self.num_column_count = 0 # 数値データの列数
        
        self.data_holder = "" # 行データを一時的に保持する
        self.header_line = "" # ヘッダーデータ行
        
        self.condition_flag = 0 # 上記参照
        self.df: Optional[pd.DataFrame] = None # データフレーム
        
        
    def analyze_data(self): # 全体の統合処理
        print("Execute analyze_data Method")
        # ★条件出しの処理
        # ファイルの最終行の行番号を取得
        try:
            file_path = self.file_path
            self.last_line_number = self.count_lines(file_path)
        except ValueError as e: # ファイルが空の場合のエラー処理
            messagebox.showerror("error", str(e))
            sys.exit(1)
        print(f"last_line_number: {self.last_line_number}")
        # 数値データ行を探す処理
        try:
            self.find_numerical_data_row(file_path)
        except ValueError as e: # 数値データ行が見つからない場合のエラー処理
            messagebox.showerror("error", str(e))
            sys.exit(1)
        # 数値データ行から列数を取得し、列の文字数をリスト化する処理
        self.parse_data_line() # 列の幅をリスト化したものを取得
        self.df = self.data_reader(self.file_path) # データ読み込み処理
        self.compare_header_and_data()  # 数値データ列数とヘッダー項目数が合致するかをチェックする処理

        # ★データの読み込み処理
        # データ読み込み処理                 
        if self.condition_flag == 1:  # 数値データ行が最初の行の場合(ヘッダー無しと推測, 各列名を入力)
            print("Execute process_condition_1 Method")
            self.columns_names_list = self.prompt_for_header(root)
            if self.columns_names_list == []:            
                self.condition_flag = 4 # 列名が入力されなかった場合、アルファベット順に列ヘッダーを付ける
                self.process_condition_4()
                return self.df
            else:
                self.add_column_names(self.df, self.columns_names_list)
                return self.df

        elif self.condition_flag == 2:  # 数値データ行が最初の行以外の場合(ヘッダー有りと推測)
            print("Execute process_condition_2 Method")
            self.df = self.add_column_names(self.df, self.data_header_list)
            return self.df
            
        elif self.condition_flag == 3:  # 数値データ行が最初の行以外の場合(ヘッダー無しと推測)
            print("Execute process_condition_3 Method")
            self.columns_names_list = self.prompt_for_header(root)
            if self.columns_names_list == []:
                self.condition_flag = 4
                self.process_condition_4()
                return self.df
            else:
                self.add_column_names(self.df, self.columns_names_list)
                return self.df  

        elif self.condition_flag == 4: #  数値データ行が最初の行以外の場合(ヘッダー無し, 各列にアルファベットを割り当てる)
            print("Execute process_condition_4 Method")
            self.process_condition_4()
            return self.df
        else:
            print("条件に合致しませんでした")
            sys.exit(1)
            
    def process_condition_4(self): # 数値データ行が最初の行以外の場合(ヘッダー無し, 各列にアルファベットを割り当てる)
        print("Execute process_condition_4 Method")
        self.df = self.assign_default_headers()
        return self.df
    
    def data_reader(self, file_path) ->pd.DataFrame: # データ読み込み処理
        print("Execute data_reader Method")
        print(f"file_path: {file_path}")
        print(f"self.data_start_line_number: {self.data_start_line_number}")
        self.file_path = file_path # ファイルパスを取得
        self.df = pd.read_csv(
            self.file_path,
            delim_whitespace=True,
            header=None,
            skiprows=self.data_start_line_number,
            on_bad_lines='skip'  # 問題のある行をスキップ
        )
        print(f"df: {self.df.head()}")
        self.df = self.df.dropna(how='all')  # 全ての列がNaNの行を削除する
        print(f"df: {self.df.head()}")
        return self.df # データフレームを返す

    def find_numerical_data_row(self,file_path): # 数値データ行を探す処理 type:tuple
        print("Execute find_numerical_data_row Method")
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
                self.destruction_line.append(line) # 数値データ行でない行を破棄予定行リストに追加                
                self.header_line = self.data_holder # 前に読み込んだ行をヘッダーデータ行として保持する               
                self.data_holder = line # 現在の行を一時的に保持する
                if self.contains_number(): # 現在の行に数値が含まれているとき、Tureを返す → 数値データ行と判定
                    self.data_start_line_number = i # 数値データ行の行番号を取得
                    if self.data_start_line_number == 0 and self.destruction_line[0] in r'\.\,\-\:': # 数値データ行が最初の行の場合
                        self.condition_flag = 1 # 数値データ行が最初の行の場合、1を返す
                        break # ループを抜ける
                    self.parse_header() # 直前に保持していた行（ヘッダー行）をリスト化して保存 self.data_header_list
                    break # ループを抜ける
                elif i == self.last_line_number:
                    raise ValueError("数値データ行が見つかりませんでした")
                else:
                    continue
        return self.data_start_line_number, self.data_header_list, self.data_holder # 数値データ行の行番号とヘッダーリスト、数値行を返す
    
    def parse_data_line(self) ->list: # 数値データ行から列数を取得し、列の文字数をリスト化する処理
        print("Execute parse_data_line Method")
        
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
        self.col_specs = [(start, end - start) for start, end in list_of_column_widths]
        
        return self.col_specs  # 列の幅をリスト化したものを返す
    
    def check_for_header(self) -> bool: # 最初の行から1列目を取り出し、日付としてパースできるかどうかをチェックする処理
        print("Execute check_for_header Method")
        first_column_value = self.data_header_list[0]
        try:
            # 日付としてパースを試みる
            parse(first_column_value)
            # パースに成功した場合、これはデータ行である
            return False
        except ValueError:
            # パースに失敗した場合、これはヘッダー行である
            return True
        
    def compare_header_and_data(self)->bool: # 数値データ列数とヘッダー項目数が合致するかをチェックする処理
        print("Execute compare_header_and_data Method")
        self.num_column_count = len(self.col_specs) # 数値データ列数を取得
        header_count = len(self.data_header_list) # ヘッダー項目数を取得
        if self.num_column_count == header_count:
            self.condition_flag = 2 # 数値データ列数とヘッダー項目数が合致する場合、2を返す
            return True # 数値データ列数とヘッダー項目数が合致する場合、Trueを返す
        else:
            self.condition_flag = 3 # 数値データ列数とヘッダー項目数が合致しない場合、3を返す
            return False # 数値データ列数とヘッダー項目数が合致しない場合、Falseを返す
    
    def prompt_for_header(self,root) ->list: # GUIを立ちあげて、列名入力を促す処理
        print("Execute prompt_for_header Method")
        root = tk.Tk()
        root.title('列名を入力してください')
        root.geometry('200x325')
        num_columns = len(self.col_specs)
        self.entries = []
        self.columns_names_list = []
        for i in range(num_columns):
            Label(root, text=f'列{i+1}の名前:').grid(row=i, column=0)
            entry = Entry(root)
            entry.grid(row=i, column=1)
            self.entries.append(entry)
        submit_btn = Button(root, text='決定', command=self.on_submit)
        submit_btn.grid(row=num_columns, column=1)
        root.mainloop()
        print(f"self.columns_names_list: {self.columns_names_list[:]}")
        return self.columns_names_list # 列ヘッダー名を返す
   
    def on_submit(self): # 決定ボタンが押されたら、列名を取得する
        print("Execute on_submit Method")
        self.columns_names_list = [entry.get() for entry in self.entries if entry.get().strip()]
        if self.columns_names_list == []:
            self.condition_flag = 4 # 列名が入力されなかった場合、アルファベット順に列ヘッダーを付ける
        print(f"self.columns_names_list: {self.columns_names_list[:]}")
        root.destroy()
   
    def add_column_names(self, df, column_names:list ) ->Optional[pd.DataFrame] : # 列名をデータフレームに追加
        print("Execute add_column_names Method")
        df = self.df
        df.columns = column_names # 列名をデータフレームに追加
        self.df = df
        return self.df
    
    def assign_default_headers(self) ->Optional[pd.DataFrame]: # 列名不明の場合、アルファベット順に列ヘッダーを付ける処理
        print("Execute assign_default_headers Method")
        # 最初の列を'DATETIME'として、残りの列にはアルファベットを割り当てます。
        # DataFrameの列数を取得
        if self.df is not None:
            n_cols = len(self.df.columns)
        else:
            n_cols = len(self.col_specs)
            
        # アルファベットリストを生成
        alphabet = list(string.ascii_uppercase) # string.ascii_uppercaseはアルファベット大文字のリストを返す
        
        # DataFrameの列数が26を超える場合、AA, AB, ... といった形式で列名を拡張
        #extended_alphabet = []
        #for first in ['', *alphabet]: # 空白文字を追加
        #    for second in alphabet: # アルファベットを追加
        #        extended_alphabet.append(first + second) # 空白文字とアルファベットを組み合わせてリスト化
        #        if len(extended_alphabet) == n_cols-1: # DataFrameの列数が26を超える場合、AA, AB, ... といった形式で列名を拡張
        #            break # ループを抜ける
        #    if len(extended_alphabet) == n_cols-1: # DataFrameの列数が26を超える場合、AA, AB, ... といった形式で列名を拡張
        #        break # ループを抜ける
        # 最初の列に'DATETIME'を設定し、残りの列にアルファベットを割り当てる
        #column_names = ['DATETIME'] + extended_alphabet        
        #self.df.columns = column_names

        # アルファベットを拡張して列名のリストを作成
        extended_alphabet = ['DATETIME'] + [letter for i, letter in enumerate(alphabet, start=1) if i < n_cols]
        # もし26列以上ある場合、AA, AB, ... のようにして列名を作成
        if n_cols > 26:
            extended_alphabet += [a + b for a in alphabet for b in alphabet][:n_cols - 26]
        # 最初の列に'DATETIME'を設定し、残りの列にアルファベットを割り当てる
        if self.df is not None:
            self.df.columns = pd.Index(extended_alphabet)
        else:
            self.df = pd.DataFrame(columns=extended_alphabet)
        return self.df        

    def contains_number(self)-> bool: # 数値が含まれている行をチェックする関数
        print("Execute contains_number Method")
        if "█" in self.data_holder: # "█"が含まれていたらFalseを返す
            return False
        return bool(re.search(r'\d', self.data_holder)) # 数値が含まれていたらTrueを返す(数値じゃなかったらFalseを返す)

    def parse_header(self) ->list: # 一番多い文字を区切り文字として、ヘッダー名をリスト化する処理
        print("Execute parse_header Method")
        # collections.Counterを使用して各文字の出現回数を数えます。
        line_counter = len(self.destruction_line) # 破棄予定行リストの行数を取得
        if line_counter == 0: # 破棄予定行リストが空の場合
            self.data_header_list = []
            return self.data_header_list
        for i in range(-2, -line_counter-1, -1): # 破棄予定行リストの行数分、ループ
            self.header_line = self.destruction_line[i] # 破棄予定行リストの最後の行から順にヘッダー行として取得
            if self.destruction_line[i] is not None: # 破棄予定行リストの最後の行が空でない場合
                counter = Counter(self.header_line)
                # 最も多い文字（区切り文字）を取得します。
                delimiter = counter.most_common(1)[0][0]
                # その文字を無視して残りの部分からヘッダー名をリスト化します。
                # ここでは、split()メソッドを使用して行を分割します。
                self.data_header_list = [header for header in self.header_line.split(delimiter) if header]
                self.data_header_list.remove('\n')
                break
            else: # 破棄予定行リストの最後の行が空の場合
                continue
        return self.data_header_list

    def count_lines(self, file_path: str) -> int: # ファイルの行数をカウントする処理
        print("Execute count_lines Method")
        with open(file_path, 'r', encoding='utf-8') as file:
            self.all_line_number = sum(1 for _ in file)
            if self.all_line_number == 0:
                raise ValueError("ファイルが空です")
            return self.all_line_number

# 保存ファイル名を指定するクラス
class SaveFileDialog:
    def __init__(self, root, start_file_path):
        self.root = root
        self.start_file_path = start_file_path
    def save_file(self, defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))):
        # デフォルトのファイル名を指定
        defult_file_name = f"{self.start_file_path}_cal.csv"
        # ファイル保存ダイアログを表示
        file_path = filedialog.asksaveasfilename(
            defaultextension=defaultextension,
            filetypes=filetypes,
            initialfile=defult_file_name # 切出し日ファイル名を指定
            )
        return file_path

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
    if processor.df is not None:
        print(processor.df.head())
    else:
        print("DataFrame is None")
        sys.exit(1)
    df = processor.df
    
    save_file_dialog = SaveFileDialog(root, file_path)
    save_file_path = save_file_dialog.save_file()
    
    if save_file_path:
        print(f"Chosen file path for saving: {save_file_path}")
    try:
        # DataFrameをCSVファイルとして保存
        df.to_csv(save_file_path, index=False)
        print("Data successfully saved.")
        messagebox.showinfo("情報", "切出しデータを保存しました。")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")









