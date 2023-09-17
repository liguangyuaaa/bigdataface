import concurrent.futures
import re

# 正则表达式模式，用于匹配包含日期和HTTP状态码的行
pattern = re.compile(r'\[(\d{2}/\w+/\d{4}):(\d{2}:\d{2}:\d{2} \+\d{4})\] ".+" (\d{3}) ')


# 处理单个文件块的函数
def process_log_chunk(chunk, target_date):
    total_requests = 0
    successful_requests = 0
    for line in chunk:
        match = pattern.search(line)
        if match:
            date, _, status_code = match.groups()
            if date == target_date:
                total_requests += 1
                if status_code.startswith('2'):  # HTTP状态码以2开头表示成功请求
                    successful_requests += 1
    return total_requests, successful_requests


# 处理日志文件
def process_log_file(log_file, target_date, batch_size=1000, num_threads=4):
    total_requests = 0
    successful_requests = 0
    with open(log_file, 'r') as file:
        chunk = []  # 用于存储当前批次的行
        for line in file:
            chunk.append(line)  # 将行添加到当前批次
            if len(chunk) >= batch_size:
                # 当批次大小达到1000行时，使用线程池并行处理当前批次
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                    results = list(executor.map(process_log_chunk, [chunk], [target_date]))
                    for total, successful in results:
                        total_requests += total
                        successful_requests += successful
                chunk = []
        if chunk:
            # 处理文件末尾可能不足1000行的剩余行
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                results = list(executor.map(process_log_chunk, [chunk], [target_date]))
                for total, successful in results:
                    total_requests += total
                    successful_requests += successful

    return total_requests, successful_requests


if __name__ == "__main__":
    log_file = 'log_file.log'
    target_date = '28/Feb/2019'
    num_threads = 4  # 线程数
    total_requests, successful_requests = process_log_file(log_file, target_date, num_threads=num_threads)

    if total_requests > 0:
        success_ratio = (successful_requests / total_requests) * 100
        print(f"时间: {target_date}")
        print(f"总数: {total_requests}")
        print(f"请求成功数据: {successful_requests}")
        print(f"成功占比: {success_ratio:.2f}%")
    else:
        print(f"无效: {target_date}")
