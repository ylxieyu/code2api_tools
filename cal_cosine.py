import re
import numpy as np
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# 关键词统计和词频统计
# 统计文件中关键词和词频
# return: {word_1: (line_id, num), word_2 : (line_id, num)}
# def get_id_file(resfile):
#     file_dict = {}  # 把整个文件的词统计为一个字典
#     with open(resfile, 'r') as res:
#         for i, line in enumerate(res.readlines()):
#             # 接下来对每一行进行操作
#             line = line.rstrip().rstrip('\n')  # 去头尾空白以及换行符
#             line_id = line.split('\t')[0]
#             line_sentence = line.split('\t')[1]
#             line_sentence = re.split(r'[\-\\_ .;<>()"\n+/?:&=,]', line_sentence)  # 按特殊符号分隔
#             # line = [i for i in line if i.rstrip() != '' or len(i.rstrip()) != 0]  # 得到每一行的分词
#             num = []
#             for word in line_sentence:
#                 if word != '':
#                     num.append(word)
#             file_dict[i] = (line_id, num)
#         # file_dict = sorted(file_dict.items(), key=lambda line_dict: line_dict[1], reverse=True)  # 字典按键值降序排序
#     return file_dict


def count(resfile_1, resfile_2):
    file_list = []  # 把整个文件的词统计为一个列表
    res1_dict, res2_dict = {}, {}
    with open(resfile_1, 'r') as res_1, open(resfile_2, 'r') as res_2:
        for i, line in enumerate(res_1.readlines()):
            # 接下来对每一行进行操作
            line = line.rstrip().rstrip('\n')  # 去头尾空白以及换行符
            line_id = line.split('\t')[0]
            line_sentence = line.split('\t')[1]
            line_sentence = re.split(r'[\-\\_ .;<>()"\n+/?:&=,]', line_sentence)  # 按特殊符号分隔
            # line = [i for i in line if i.rstrip() != '' or len(i.rstrip()) != 0]  # 得到每一行的分词
            num = ''
            num_ = []
            for word in line_sentence:
                if word != '':
                    num += word + ' '
                    num_.append(word)
            file_list.append(num)
            res1_dict[i] = (line_id, num_)
        for i, line in enumerate(res_2.readlines()):
            # 接下来对每一行进行操作
            line = line.rstrip().rstrip('\n')  # 去头尾空白以及换行符
            line_id = line.split('\t')[0]
            line_sentence = line.split('\t')[1]
            line_sentence = re.split(r'[\-\\_ .;<>()"\n+/?:&=,]', line_sentence)  # 按特殊符号分隔
            # line = [i for i in line if i.rstrip() != '' or len(i.rstrip()) != 0]  # 得到每一行的分词
            num = ''
            num_ = []
            for word in line_sentence:
                if word != '':
                    num += word + ' '
                    num_.append(word)
            file_list.append(num)
            res2_dict[i] = (line_id, num_)
    return file_list, res1_dict, res2_dict


# 统计每一行出现的关键词和词频
# return: {id_1: {word_1: num}, id_2: {word_2: num}}
# def count_row(resfile):
#     result_dict = {}  # 结果返回为dict()
#     file_dict = count(resfile)
#     with open(resfile, 'r') as res:
#         for line in res.readlines():
#             words = set()  # 记录每一行出现了哪些单词
#             # 接下来对每一行进行操作
#             line = line.rstrip().rstrip('\n')  # 去头尾空白以及换行符
#             line_id = line.split('\t')[0]
#             line_sentence = line.split('\t')[1]
#             line_sentence = re.split(r'[\- .;<>()"\n+/?:&=,_|\\]', line_sentence)  # 按特殊符号分隔
#             # line = [i for i in line if i.rstrip() != '' or len(i.rstrip()) != 0]  # 得到每一行的分词
#             for word in line_sentence:
#                 if word != '' and file_dict.__contains__(word):
#                     words.add(word)
#             line_dict = {}
#             for item in words:
#                 line_dict[item] = file_dict[item]
#             line_dict = sorted(line_dict.items(), key=lambda x: x[1], reverse=True)
#             result_dict[line_id] = line_dict
#     return result_dict

train_file = ['../cosine/train.token.nl', '../cosine/train.token.API', '../cosine/1.txt']  # 157
test_file = ['../cosine/test.token.nl', '../cosine/test.token.API', '../cosine/2.txt']  # 243
target_file = '../cosine/target_cosine.API'
# 按cosine 值top5计算
def main():
    file, id_file_train, id_file_test = count(train_file[0], test_file[0])

    Tf = TfidfVectorizer(use_idf=True)
    Tf.fit(file)
    corpus_array = Tf.transform(file).toarray()

    result_dict = {}
    for i in range(len(id_file_train)-1, len(file)-1):
        # 针对每一个test
        tmp_i = np.array([corpus_array[i]])
        temp_dict = {}
        for j in range(len(id_file_train)):
            tmp_j = np.array([corpus_array[j]])
            cosinValue = cosine_similarity(tmp_i, tmp_j)
            temp_dict[id_file_train.get(j)[0]] = (cosinValue[0][0], id_file_train.get(j)[1]) # {id: (cos, train_text)}
        temp_dict = sorted(temp_dict.items(), key=lambda x:x[1][0], reverse=True)  # 157项
        # a =id_file_test.get(i-len(id_file_train)+1)[1]
        result_dict[id_file_test.get(i-len(id_file_train)+1)[0]] = (temp_dict, id_file_test.get(i-len(id_file_train)+1)[1])  # {test_id: (dict, test_text)}

    # 计算bleu
    result_ = []
    for key, value in result_dict.items():  # 0-243
       #  test_train_score = []
        test_sentence = value[1]
        best_socre, best_id = 0, 0
        for i in range(5):
            train_sentence = value[0][i][1][1]
            chencherry = SmoothingFunction()
            BLEUscore = sentence_bleu([train_sentence], test_sentence, smoothing_function=chencherry.method1)
            if best_socre <= BLEUscore:
                best_socre = BLEUscore
                best_id = value[0][i][0]
        result_.append(str(key)+'\t'+str(best_id)+'\t'+str(best_socre))
    with open('D:\\test_train_score.txt', 'w', newline='') as b:
       for i in result_:
           b.write(i+'\n')

# 生成api文件
def getAPIfromTXT():
    with open(train_file[1], 'r') as a, open('D:\\test_train_cosine.txt', 'r') as b, open(target_file, 'w', newline='') as c:
        a_dict = {}
        api_id = []
        result_ = []
        for line in a.readlines():
            line = line.rstrip().rstrip('\n')  # 去头尾空白以及换行符
            line_id = line.split('\t')[0]
            line_sentence = line.split('\t')[1]
            a_dict[line_id] = line_sentence
        for line in b.readlines():
            line = line.rstrip().rstrip('\n')  # 去头尾空白以及换行符
            line_id = line.split('\t')[1]
            api_id.append(line_id)
        for i in api_id:
            result_.append(a_dict.get(i))
        for j in result_:
            if j is None:
                c.write('<UNK>\n')
            else:
                c.write(j + '\n')


# 按cosine值 top1 计算
def main_cosine():
    file, id_file_train, id_file_test = count(train_file[0], test_file[0])

    Tf = TfidfVectorizer(use_idf=True)
    Tf.fit(file)
    corpus_array = Tf.transform(file).toarray()

    result_dict = {}
    result_ = []
    for i in range(len(id_file_train) - 1, len(file) - 1):
        # 针对每一个test
        tmp_i = np.array([corpus_array[i]])
        temp_dict = {}
        for j in range(len(id_file_train)):
            tmp_j = np.array([corpus_array[j]])
            cosinValue = cosine_similarity(tmp_i, tmp_j)
            temp_dict[id_file_train.get(j)[0]] = (cosinValue[0][0], id_file_train.get(j)[1])  # {id: (cos, train_text)}
        temp_dict = sorted(temp_dict.items(), key=lambda x: x[1][0], reverse=True)  # 157项
        # a =id_file_test.get(i-len(id_file_train)+1)[1]
        # result_dict[id_file_test.get(i - len(id_file_train) + 1)[0]] = (temp_dict, id_file_test.get(i - len(id_file_train) + 1)[1])  # {test_id: (dict, test_text)}
        result_.append(str(id_file_test.get(i - len(id_file_train) + 1)[0]) + '\t' + str(temp_dict[0][0]) + '\t' + str(temp_dict[0][1][0]))
    with open('D:\\test_train_cosine.txt', 'w', newline='') as b:
       for i in result_:
           b.write(i+'\n')

if __name__ == '__main__':
    # main()
    getAPIfromTXT()
    # main_cosine()
