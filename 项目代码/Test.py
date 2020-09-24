# author:Boyle time:2020/9/25
from util.cal_util import cal_repeat_rate_0
from util.file_util import *

def test():
    paper_a = load_file("dataset/orig.txt")
    paper_b = load_file("dataset/orig_0.8_del.txt")
    cal_repeat_rate_0(paper_a, paper_b)

if __name__=="__main__":
    test()
