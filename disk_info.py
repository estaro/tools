# -*- coding: utf-8 -*-
"""
    disk_info.py

    ディスクの使用容量を一覧化するスクリプトです。

"""
import shutil
import os
import logging
logger = logging.getLogger(__name__)
fmt = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(format=fmt, level=logging.DEBUG)

# フォルダをリスト化最大の深さ
MAX_DEPTH = 3

# リスト化対象のドライブレター
DRIVE_LETTER = 'DE'

# 出力ファイル
OUTPUT_FILE = './output.tsv'


def main():
    """
    メイン

    :return:
    """

    folder_tree = {}
    for drive in list(DRIVE_LETTER):
        # --------------------------------------
        # ドライブ単位の処理
        # --------------------------------------
        drive_path = drive + '://'
        with os.scandir(drive_path) as it:
            folder_tree[drive] = {'folders': []}
            for entry in it:
                if exclude_file(entry.name):
                    continue
                elif entry.is_file():
                    pass
                elif entry.is_dir():
                    folder_tree[drive]['folders'].append(folder_info(entry.path))
        # ドライブの使用量は別に取得する
        usage = shutil.disk_usage(drive_path)
        folder_tree[drive]['total'] = usage[0]
        folder_tree[drive]['used'] = usage[1]
        folder_tree[drive]['free'] = usage[2]

    # ファイル書き込み
    write_string = []
    logger.debug(folder_tree)
    for root in folder_tree:
        tabs = ''
        for i in range(0, MAX_DEPTH):
            tabs += '\t'
        write_string.append(root + tabs + format_size(folder_tree[root]['used']) + '\t' + format_size(folder_tree[root]['free']) + '\n')
        for folder in folder_tree[root]['folders']:
            write_string.extend(rec_format_folder(folder, 1))

    with open(OUTPUT_FILE, mode='w') as f:
        f.writelines(write_string)


def folder_info(path):
    """
    1フォルダの情報を取得する

    :param path:
    :return:
    """

    folders = {'path': path, 'size': 0, 'folders': []}
    try:
        with os.scandir(path) as it:
            for entry in it:
                # 除外ファイルのスキップ
                if exclude_file(entry.name):
                    continue
                # ファイルの場合はサイズを加算する
                elif entry.is_file(follow_symlinks=False):
                    folders['size'] += entry.stat(follow_symlinks =False).st_size
                # ディレクトリは再帰で取得する
                elif entry.is_dir():
                    folders['folders'].append(folder_info(entry.path))
                else:
                    logging.warning('-- ' + entry.path)
    except:
        logging.warning("read error. " + path)

    return folders


def rec_format_folder(folder, depth):
    """
    フォルダ単位の出力制御

    :param folder:
    :param depth:
    :return:
    """
    result = []

    format_str = ''
    for i in range(0, depth):
        format_str += '\t'
    format_str += folder['path']
    for i in range(0, MAX_DEPTH - depth):
        format_str += '\t'
    format_str += format_size(folder['size'])
    result.append(format_str + '\n')

    # チェック
    depth += 1
    if depth >= MAX_DEPTH or 'folders' not in folder:
        return result

    # 次の階層
    for folder in folder['folders']:
        result.extend(rec_format_folder(folder, depth))

    return result


def format_size(size):
    """
    使用量の表示

    :param size:
    :return:
    """
    # 単位はGByteとする
    f_size = size / 1024 / 1024 / 1024
    f_size = round(f_size, 3)
    return str(f_size)


def exclude_file(name):
    """
    除外する条件

    :param name:
    :return:
    """
    if 'System Volume Information' in name:
        return True
    if '$RECYCLE.BIN' in name:
        return True

    return False


if __name__ == "__main__":
    logger.info('start -----------')
    main()
    logger.info('end -----------')
