# 工具模块
# 存放各种常用操作的函数
import logging
import csv
import re
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def check_empty_value(file_name):
    # 输入：file_name
    # 文件列结构： [id] + '\t' + [value]
    # 目的是检查value是否为空|是否出现空行
    # 输出：'empty value id: ' + [id] + '\n' + 'empty line num: ' + i
    with open(file_name, 'r') as fn:
        count = 0  # 文件总行数计数
        empty_value_id_list, empty_line_num_list = [], []
        for i, line in enumerate(fn.readlines()):
            count = i
            question_id = line.strip().split('\t')[0]
            try:
                line.strip().split('\t')[1]
            except IndexError:
                empty_value_id_list.append(question_id)
            tmp = str(line.strip().replace('\n', ''))
            if tmp.isspace():
                empty_line_num_list.append(i + 1)
        logging.info('function: check_empty_value\nfile name: ' + file_name +
                     '\nfile lines: ' + str(count + 1) +
                     '\nempty value id: ' + empty_value_id_list.__str__() +
                     '\nempty line num: ' + empty_line_num_list.__str__())


def get_dict_from_csv(file_name, key_column, value_column):
    # file_name  csv文件路径
    # key_column csv文件中能作为字典key值的列编号
    # value_num  csv文件中能作为字典value值的列编号
    # 目的是将csv文件中特定的两列转化为字典结构
    # return: dict{}
    with open(file_name, 'r') as fn:
        csv_reader = csv.reader(fn)
        count = 0  # 文件总行数计数
        r_dict = {}
        for i, line in enumerate(csv_reader):
            line = list(line)
            question_id = line[key_column]
            ast_seq = line[value_column]
            if question_id not in r_dict.keys():
                # question_id 是第一次出现
                if ast_seq != 'nal' and ast_seq != 'other language':
                    r_dict[question_id] = ast_seq
            else:
                if ast_seq != 'nal' and ast_seq != 'other language':
                    tmp = r_dict[question_id]
                    tmp += ('\n' + ast_seq)
                    r_dict[question_id] = tmp
            count = i
        logging.info('function: get_dict_from_csv\nfile name: ' + file_name +
                     '\nfile lines: ' + str(count + 1))
        return r_dict


def parse_ast(ast_seq):
    # ast_seq  待解析的ast节点
    # return: str
    p = re.compile(r'Class: ([\w]*)')
    re_ast = p.findall(ast_seq)
    str_code = ''
    unk_num = 0
    for item in re_ast:
        if 'zzz' in item or 'ZZZ' in item:
            unk_num += 1
        else:
            str_code += item + ' '
    if len(str_code.strip()) == 0 or str_code.isspace():
        for nu in range(unk_num):
            str_code += 'UNK '
    if len(str_code.strip()) == 0 or str_code.isspace():
        str_code = 'UNK'
    return str_code


def parse_node2token(file_name, target_file, key_column, value_column):
    # file_name  csv文件路径
    # target_file 存放结果的文件
    # key_column csv文件中能作为字典key值的列编号
    # value_num  csv文件中能作为字典value值的列编号
    # 目的是解析ast.csv文件中ast 节点, 将结果保存为.code文件
    r_dict = get_dict_from_csv(file_name, key_column, value_column)
    with open(target_file, 'w', newline='') as tf:
        for key, value in r_dict.items():
            tf.write(str(key) + '\t' + parse_ast(value) + '\n')
        logging.info('function: parse_node2token\nfile name: ' + file_name)


def count_words(file_name):
    # file_name  文件路径
    # 目的是统计文件中每一行的词频
    # 输出: 'line-words avg: ' + [avg] + '\nline num of (words < 50): ' + [num] +
    # '\nline num of (words < 100): ' + [num] + '\nline num of (words < 200): ' + [num]
    r_dict = {}
    with open(file_name, 'r') as fn:
        count = 0  # 文件总行数计数
        for i, line in enumerate(fn.readlines()):
            tmp = line.strip().split('\t')
            question_id = tmp[0]
            sentence = tmp[1]
            words = re.split('[, ?;/:%#]', sentence)
            r_dict[question_id] = len(words)
            count = i + 1
    num_50, num_100, num_200 = 0, 0, 0
    for key, value in r_dict:
        if value < 50:
            num_50 += 1
        if value < 100:
            num_100 += 1
        if value < 200:
            num_200 += 1
    logging.info('function: count_words\nfile name: ' + file_name +
                 '\nfile lines: ' + str(count + 1) +
                 '\nline-words avg: ' + str(sum(r_dict.values()) / len(r_dict)) +
                 '\nline num of (words < 50): ' + str(num_50) +
                 '\nline num of (words < 100): ' + str(num_100) +
                 '\nline num of (words < 200): ' + str(num_200))


def count_rows(file_name):
    # 目的是检查文件的行数
    with open(file_name, 'r') as fn:
        r_list = list(fn.readlines())
        logging.info('function: count_rows\nfile lines: ' + str(len(r_list)))


def cal_eval(ref, hypothesis, steps=100):
    # ref: valid.token.api的存放路径
    # hypothesis: 存放out文件的eval路径
    # steps: yaml文件内设置的步长，即多久存一次out文件
    # 目的是绘出precision和recall的变化曲线图&输出最优的位置
    files = os.listdir(hypothesis)
    file_dict = {}
    for file in files:
        key = int(file[6:-4])
        file_dict[key] = file
    file_dict = sorted(file_dict.items(), key=lambda x: x[0])
    # 将验证的数据放入列表valid
    valid = []
    with open(ref, 'r') as f:
        for line in f.readlines():
            line = line.strip().replace('\n', '').split('\t')[1]
            valid.append(line)
    precisions, recalls = [], []  # 将每一个precision和recall的结果存放
    for n in range(len(file_dict)):
        file = file_dict[n][1]
        file_path = os.path.join(hypothesis, file)
        with open(file_path, 'r') as f:
            counts, recall = [], []
            for i, line in enumerate(f.readlines()):
                _line = line.strip().replace('\n', '').split(' ')  # 每一个out文件的每一行的分词
                count = 0
                for j in _line:
                    if j in valid[i]:
                        count += 1
                recall.append(count / len(valid[i].split(' ')))
                counts.append(count / len(_line))
            precision = sum(counts) / len(valid)
            recall = sum(recall) / len(valid)
            precisions.append(precision)
            recalls.append(recall)
    x_out = np.array([i * steps for i in range(len(files))])
    y_precisions = np.array(precisions)
    y_recalls = np.array(recalls)
    max_precision = y_precisions.max()
    max_precision_index = precisions.index(max_precision)
    max_recall = y_recalls.max()
    max_recall_index = recalls.index(max_recall)
    df_1 = pd.DataFrame(y_precisions, index=x_out, columns=['precision'])
    df_2 = pd.DataFrame(y_recalls, index=x_out, columns=['recall'])
    logging.info('function: cal_eval\nmax_precision: ' +
                 str(max_precision_index * steps) + '\t' + str(max_precision) +
                 '\nmax_recall: ' + str(max_recall_index * steps) + '\t' + str(max_recall))
    sns.relplot(data=df_1, kind='line')
    sns.relplot(data=df_2, kind='line')
    plt.show()


if __name__ == '__main__':
    # 日志
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    lf = logging.FileHandler('../log/tools_log.txt', encoding='utf-8')
    ls = logging.StreamHandler()
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[lf, ls])
    logging.info('choose your tool function:')

    # function: check_empty_value
    # check_empty_value('../data/20190309_android_so_ori/generate_file_code/text.code')

    # function: parse_node2token
    # parse_node2token()

    # function: count_words
    # count_words()

    # function: count_rows
    # count_rows()

    # function: cal_eval
    cal_eval('../data/valid/valid.token.api', '../data_pre/model/multi_attention_sum/eval', steps=200)
