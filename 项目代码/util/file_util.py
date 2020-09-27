# author:Boyle time:2020/9/23
import os
import sys
import numpy as np

def load_file(file_path):
    """
    加载txt文件，并以列表类型输出
    :param file_path: txt文件路径
    :return:
        txt文件的字符序列
        {“parags": "包含txt文件的字符序列的列表"}
    :raise:
        IOError: An error occurred reading the txt file
    """
    try:
        parags = []
        with open(file_path, 'r+', encoding='utf-8') as f:
            for line in f.readlines():  # 按行读取每行
                temp = line[:-1].split('。')
                temp = list(map(
                    lambda x: x.replace('\u3000', '').replace('\t', '').replace('  ', '').replace('\r', ' '),
                    temp
                ))
                parags.extend(line[:-1].split('。'))  # 切片去掉换行符，再以‘。’分割字符串 ，得到一个列表
    except:
        raise IOError("An error occurred reading the txt file")
    return parags

def save_file(file_path, result):
    """
    将字符序列存储到txt文件中
    :param file_path: txt文件路径
    :param result: 计算结果字段，内容包括论文的重复率以及相似段落
    :return:
        无
    :raise:
        IOError: An error occurred saveing the txt file
    """
    try:
        with open(file_path, "w") as f:
            f.writelines("重复率：" + str(round(result["repeat_rate"] * 100, 2)) + "%\n")
            for i in range(result["sentence_num"]):
                f.writelines("\n----------段落"+str(i+1)+"----------\n")
                f.writelines("原段落：\n" + result[i + 1][0] + "\n")
                f.writelines("抄袭段落：\n" + result[i + 1][1] + "\n")
    except Exception as e:
        print(e.args)
        raise IOError("An error occurred saving the txt file")

