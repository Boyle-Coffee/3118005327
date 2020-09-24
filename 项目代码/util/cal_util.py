# author:Boyle time:2020/9/23
import jieba
import jieba.analyse
import numpy as np

from util.config import config
def hamming_dis(simhash1, simhash2):
    """
    计算汉明距离
    :param simhash1: 第一个字符序列的SimHash值序列，NumPy数组类型
    :param simhash2: 第二个字符序列的SimHash值序列，NumPy数组类型
    :return:
        汉明距离
    """
    dis = np.sum(simhash1 != simhash2)
    return dis

def str2hash(ori_str):
    """
    计算字符的哈希值
    :param ori_str: 原始字符
    :return:
        字符的哈希值
    """
    if ori_str == '' or ori_str.replace(' ', '') == '':
        return 0
    hash_value = ord(ori_str[0])<<7
    m = 1000003
    mask = 2 ** 128 - 1
    for c in ori_str:
        hash_value = ((hash_value*m)^ord(c) ^ mask)
    hash_value ^= len(ori_str)
    hash_value = -2 if hash_value==-1 else hash_value
    hash_value = bin(hash_value).replace('0b', '').zfill(64)[-64:]
    return str(hash_value)

def cal_simhash(content):
    """
    计算对应内容的SimHash值
    :param content: 原始字符序列
    :return:
        对应的SimHash值，NumPy数组类型
    """
    jieba.analyse.set_stop_words("util/stopwords.txt")  # 去除停用词
    key_words = jieba.analyse.extract_tags(
        content, topK=20, withWeight=True, allowPOS=())  # 根据 TD-IDF 提取关键词
    if len(key_words) < config.least_key_words: # 少于设定的最少关键词数量，放弃该段文字
        return None
    hash_series = []
    for kw, weight in key_words:
        weight = int(weight * 20)
        try:  # 异常处理，当计算哈希值失败时，跳过该关键词
            kw_hash = str2hash(kw)  # 计算该关键词的哈希值
            hash_c = (np.array(list(map(int, kw_hash)))-0.5)*2  # 转换为1/-1序列
        except:
            continue
        hash_series.append(hash_c*weight)  # 哈希序列加权相加
    if not hash_series:  # 编码读取失败
        return "10"
    simhash_series = np.sum(np.array(hash_series),axis=0)
    simhash_series = (simhash_series>0).astype(np.int32)
    return simhash_series

def cal_repeat_rate(orig_paper, orig_modify_paper):
    """
    根据SinHash算法计算论文的重复率
    :param orig_paper: 原论文
    :param orig_add_paper: 抄袭论文
    :return:
        {"result": "保留计算结果的字典，包括两篇论文的重复率和重复的段落/
                        例如，/
                        {"repeat_rate": 0.87,/
                         1: ["原文段落1", "抄袭段落1"],/
                         2: ["原文段落2", "抄袭段落2"],/
                         .../
                         }
                        "
        }
        当返回负数时，表示在计算过程中出现错误，不同数值对应不同错误，具体参考本项目设计文档
    """
    orig_modify_paper_len, copy_word_num = 0, 0
    result = {}
    result_index = 1
    orig_modify_simhash = []
    orig_modify_temp = []
    for orig_modify_div in orig_modify_paper:
        orig_modify_paper_len += len(orig_modify_div)
        modify = False  # 记录该段落是否是修改的
        orig_modify_div_simhash = cal_simhash(orig_modify_div)
        if orig_modify_div_simhash is None:  # 当返回空值，说明该段落为空，跳过该段落
            continue
        if orig_modify_div_simhash == "10":  # 当抄袭论文编码读取失败时，返回-1
            return -1
        orig_modify_temp.append(orig_modify_div)
        orig_modify_simhash.append(orig_modify_div_simhash)
    orig_modify_simhash = np.array(orig_modify_simhash)
    orig_simhash = []
    orig_temp = []
    for orig_div in orig_paper:
        orig_div_simhash = cal_simhash(orig_div)
        if orig_div_simhash is None:
            continue
        if orig_div_simhash == "10":  # 当原论文编码读取失败时，返回-2
            return -2
        orig_temp.append(orig_div)
        orig_simhash.append(orig_div_simhash)
    orig_simhash = np.array(orig_simhash)
    sim_matrix = []
    for orig_modify_simhash_i in orig_modify_simhash:  # 生成相似矩阵，表示两篇论文不同段落SimHash值的汉明距离
        sim_matrix.append(np.sum(orig_modify_simhash_i != orig_simhash, axis=1))
    sim_matrix = np.array(sim_matrix)
    result = {}
    result_index = 1
    try:
        for i in range(sim_matrix.shape[0]):
            if np.min(sim_matrix[i]) <= config.hamming_dis_threshold:
                min_i = np.argmin(sim_matrix[i])
                copy_word_num += len(orig_modify_temp[i])  # 相似则统计相似字数
                result[result_index] = [orig_temp[min_i], orig_modify_temp[i]]
                result_index += 1
    except:
        return -3
    result["repeat_rate"] = copy_word_num/orig_modify_paper_len
    result["sentence_num"] = result_index-1
    return result

def cal_repeat_rate_0(orig_paper, orig_modify_paper):
    """
    根据SinHash算法计算论文的重复率（改进前算法）
    :param orig_paper: 原论文
    :param orig_add_paper: 抄袭论文
    :return:
        {"repeat_rate": "保留计算结果的字典，包括两篇论文的重复率和重复的段落/
                        例如，/
                        {"repeat_rate": 0.87,/
                         1: ["原文段落1", "抄袭段落1"],/
                         2: ["原文段落2", "抄袭段落2"],/
                         .../
                         }
                        "
        }
    """
    orig_modify_paper_len, copy_word_num = 0, 0
    result = {}
    result_index = 1
    for orig_modify_div in orig_modify_paper:
        orig_modify_paper_len += len(orig_modify_div)
        modify = False  # 记录该段落是否是修改的
        orig_modify_div_simhash = cal_simhash(orig_modify_div)
        if orig_modify_div_simhash is None:  # 当返回空值，说明该段落为空，跳过该段落
            continue
        if orig_modify_div_simhash == "10":  # 当抄袭论文编码读取失败时，返回-1
            return -1
        for orig_div in orig_paper:
            orig_div_simhash = cal_simhash(orig_div)
            if orig_div_simhash is None:
                continue
            if orig_div_simhash == "10":  # 当原论文编码读取失败时，返回-2
                return -2
            try:
                item_dis = hamming_dis(orig_modify_div_simhash, orig_div_simhash)
                # print(item_dis)
                if item_dis <= 17:  # 当汉明距离小于阈值时，则记录为相似段落
                    result[result_index] = [orig_div, orig_modify_div, item_dis]
                    result_index += 1
                    modify = True
            except Exception as e:
                print(e)
                return -3
        if modify:  # 当该段落相似时，则统计该段落的词数量
            copy_word_num += len(orig_modify_div)
    result["repeat_rate"] = copy_word_num/orig_modify_paper_len
    return result

