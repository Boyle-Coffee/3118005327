# author:Boyle time:2020/9/20
import sys
from util import file_util
from util import cal_util
import time

def main():

    # 解析命令行参数
    args = sys.argv
    if len(args) < 4:
        print("错误：输入参数太少")
        exit(-1)
    elif len(args) > 4:
        print("错误：输入多余参数")
        exit(-1)

    # 读取文件
    try:
        orig_file_path = args[1]
        paper_a = file_util.load_file(orig_file_path)
    except:
        print("错误：读取原论文文件时出现错误，可能是因为该路径文件不存在或者文件异常")
        exit(-1)
    try:
        orig_modify_file_path = args[2]
        paper_b = file_util.load_file(orig_modify_file_path)
    except:
        print("错误：读取待查论文文件时出现错误，可能是因为该路径文件不存在或者文件异常")
        exit(-1)

    # 计算重复率
    try:
        result = cal_util.cal_repeat_rate(paper_a, paper_b)
    except:
        print("错误：计算重复率时发生未知错误，可能是原文件异常或者输入了空文件")
        exit(-1)
    if result == -1:
        print("错误：待查论文编码读取失败")
    elif result == -2:
        print("错误：原论文编码读取失败")
    elif result == -3:
        print("错误：计算汉明距离时发生错误")
    # 保存结果
    try:
        ans_txt_path = args[3]
        file_util.save_file(ans_txt_path, result)
    except:
        print("错误：在存储结果的时候发生错误，有可能指定的路径不存在")

if __name__=="__main__":
    start_time = time.time()
    main()
    print("运行时间："+str(time.time()-start_time))
