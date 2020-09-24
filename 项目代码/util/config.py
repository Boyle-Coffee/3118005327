# author:Boyle time:2020/9/24

class simhash_mdl_config():
    # SimHash算法的参数
    least_key_words = 6  # 计算段落的最小关键词数，关键词数小于该值不做计算
    hamming_dis_threshold = 20  # 汉明距离阈值，两句SimHash值的汉明距离小于该阈值时认为两句相似

config = simhash_mdl_config()
