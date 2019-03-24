# 将code提取的几个py 文件整合在一个文件中
import os
import csv as csv
import re
from bs4 import BeautifulSoup

orig_path = '../20190309_android_so_ori/ori/'  # 需要处理的原始文件的目录
column_code_path = orig_path.replace('/ori/', '/generate_column_code/')  # 生成的文件目录
error = ['/', '<', '>', 'android:']


# 第一步处理 从<pre><code>中提取code
# 如果提取失败，则从<code>中提取--》此时不明确提取出来的东西是否是代码?暂时不加标志位
def main():
    files = os.listdir(orig_path)
    for file in files:
        absolute_file = orig_path + file
        index_ = file.find('.')
        file_name = file[:index_]
        target_absolute_file = column_code_path + file_name + '_code.csv'
        with open(absolute_file, 'r') as rf, open(target_absolute_file, 'w', newline='') as wf:
            csv_reader = csv.reader(rf)
            csv_writer = csv.writer(wf)
            count, count_null = 0, 0
            for i, line in enumerate(csv_reader):
                p = re.compile(r'<pre><code>((?:.|\n)*?)<\/code><\/pre>')
                c = re.compile(r'<code>((?:.|\n)*?)<\/code>')
                re_str = p.findall(line[3])
                line = list(line)
                line.pop(10)  # 删除空列
                if len(re_str) == 0:
                    re_c = c.findall(line[3])
                    c_str = ''
                    for item in re_c:
                        c_str += item + (' ')
                    line.append(c_str)
                    count_null += 1
                    csv_writer.writerow(line)
                else:
                    line.append(re_str[0])
                    csv_writer.writerow(line)
                count = i + 1
            print(file_name + '\t lines: ' + str(count) + '\t <code>: ' + str(count_null))


def fragmentCode(source_path, target_path):
    with open(source_path, 'r') as a, open(target_path, 'w', newline='') as b:
        csv_reader = csv.reader(a)
        csv_writer = csv.writer(b)
        for i, line in enumerate(csv_reader):
            line = list(line)
            other_column = ''
            line_list = []
            for i in range(4, len(line)):
                if len(line[i]) != 0 and line[i] != '':
                    other_column += line[i] + ' '
            line_list.append(line[0])
            line_list.append(line[1])
            line_list.append(line[2])
            line_list.append(line[3])
            line_list.append(other_column)
            tmp = ''
            if line[2] == 'jenkov':
                soup_i = BeautifulSoup(line[3])
                for m in soup_i.find_all('pre'):
                    if m['class'] == ['codebox']:
                        for string in m.strings:
                            tmp += string + ' '
                if len(tmp.strip()) == 0:
                    tmp = 'UNK'
                line_list.append(tmp)
            if line[2] == 'jodatime' or line[2] == 'math' or line[2] == 'official':
                soup_i = BeautifulSoup(line[3])
                for m in soup_i.find_all('pre'):
                    for string in m.strings:
                        tmp += string + ' '
                if len(tmp.strip()) == 0:
                    tmp = 'UNK'
                line_list.append(tmp)
            if line[2] == 'smack':
                soup_i = BeautifulSoup(line[3])
                for m in soup_i.find_all('pre'):
                    tmp += m.get_text() + ' '
                if len(tmp.strip()) == 0:
                    tmp = 'UNK'
                line_list.append(tmp)
            csv_writer.writerow(line_list)


# 提取android tu 的code
def fragmentCodeAndroid(source_path, target_path):
    with open(source_path, 'r') as a, open(target_path, 'w', newline='') as b:
        csv_reader = csv.reader(a)
        csv_writer = csv.writer(b)
        for i, line in enumerate(csv_reader):
            line = list(line)
            line_list = []
            other_column = ''
            for i in range(4, len(line)):
                if len(line[i]) != 0 and line[i] != '':
                    other_column += line[i] + ' '
            line_list.append(line[0])
            line_list.append(line[1])
            line_list.append(line[2])
            line_list.append(line[3])
            line_list.append(other_column)
            tmp = ''
            if line[2] == 'graphics' or line[2] == 'resources' or line[2] == 'text':
                soup_i = BeautifulSoup(line[3])
                for m in soup_i.find_all('pre'):
                    if '<' not in m.get_text():
                        tmp += m.get_text() + ' '
                if len(tmp.strip()) == 0:
                    tmp = 'UNK'
                line_list.append(tmp)
            if line[2] == 'data':
                soup_i = BeautifulSoup(line[3])
                for m in soup_i.find_all('code'):
                    tmp += m.get_text() + ' '
                if len(tmp.strip()) == 0:
                    tmp = 'UNK'
                line_list.append(tmp)
            csv_writer.writerow(line_list)


def iserrror(str):
    for i in error:
        if i in str:
            return False
    return True

if __name__ == '__main__':
    # main()
    # fragmentCode('../20190309_java_android_tu_ori/java_tutorial/java_fapis.csv', '../20190309_java_android_tu_ori/java_tutorial/java_fcode.csv')
    fragmentCodeAndroid('../20190309_java_android_tu_ori/android_tutorial/android_fapis.csv', '../20190309_java_android_tu_ori/android_tutorial/android_fcode.csv')
