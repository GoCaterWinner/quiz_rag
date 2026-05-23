"""
jsonl工具
"""
import json



def read_jsonl(path):
    """
    功能: 打开文件, 对里面的json文件一条一条读取
    
    输入: 文件路径
    输出: 每次读取一条, 防止数据过大造成内存过载
    """

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():

                # yield一次返回一条结果, 并且保存好当前的记录, 下次可以继续用
                yield json.loads(line)



def write_jsonl(file, path):
    """
    功能, 写入固定路径

    输入: 写入内容, 写入路径
    输出: 转成json送入文件
    """

    with path.open("a", encoding="utf-8") as f:
        file_json = json.dumps(file, ensure_ascii=False)

        f.write(file_json + "\n")
