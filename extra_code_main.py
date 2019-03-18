# 将code提取的几个py 文件整合在一个文件中
import os
import csv as csv
import re

orig_path = '../20190309_android_so_ori/ori/'  # 需要处理的原始文件的目录
column_code_path = orig_path.replace('/ori/', '/generate_column_code/')  # 生成的文件目录

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
            p = re.compile(r'<pre>((?:.|\n)*?)<\/pre>')
            # c = re.compile(r'<code>((?:.|\n)*?)<\/code>')
            re_str = p.findall(line[3])
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
            if len(re_str) == 0:
                line_list.append('UNK')
            else:
                tmp = ''
                for j in re_str:
                    tmp += j
                if line[2] == 'smack':
                    tmp = tmp.rstrip().replace('<font color="#3f7f5f">', '').replace('</font>', '')\
                        .replace('<font color="#0000ff">', '').replace('&quot;', '')
                else:
                    tmp = tmp.rstrip().replace('&quot;', '').replace('&quot,', '')\
                        .replace('&gt;', ' ').replace('&lt', '')
                line_list.append(tmp)
            csv_writer.writerow(line_list)


# 提取android tu 的code
def fragmentCodeAndroid(source_path, target_path):
    with open(source_path, 'r') as a, open(target_path, 'w', newline='') as b:
        csv_reader = csv.reader(a)
        csv_writer = csv.writer(b)
        for i, line in enumerate(csv_reader):
            p = re.compile(r'<pre>((?:.|\n)*?)<\/pre>')
            c = re.compile(r'<a href[^>]*>((?:.|\n)*?)<\/a>')  # 取超链接标签内的
            # c = re.compile(r'<code>((?:.|\n)*?)<\/code>')
            re_str = p.findall(line[3])
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
            if len(re_str) == 0:
                line_list.append('UNK')
            else:
                tmp = ''
                for j in re_str:
                    j = re.

                tmp = tmp.strip().replace('&quot;', '').replace('&quot,', '') \
                    .replace('&gt;', ' ').replace('&lt', '')
                line_list.append(tmp)
            csv_writer.writerow(line_list)

if __name__ == '__main__':
    # main()
    # fragmentCode('../20190309_java_android_tu_ori/java_tutorial/java_fapis.csv', '../20190309_java_android_tu_ori/java_tutorial/java_fcode.csv')
    fragmentCodeAndroid('../20190309_java_android_tu_ori/android_tutorial/android_fapis.csv', '../20190309_java_android_tu_ori/android_tutorial/android_fcodes.csv')
