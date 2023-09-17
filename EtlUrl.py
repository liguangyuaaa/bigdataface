import concurrent.futures
import re

# 正则表达式模式，用于匹配包含 "https://domain1.com" 的行
pattern = re.compile(r' "https://domain1\.com')


# 处理单个文件块的函数
def process_log_chunk(chunk):
    count = 0
    for line in chunk:
        if pattern.search(line):
            count += 1
    return count


# 处理日志文件
def process_log_file(log_file, batch_size=1000, num_threads=4):
    total_count = 0
    with open(log_file, 'r') as file:
        chunk = []  # 用于存储当前批次的行
        for line in file:
            chunk.append(line)  # 将行添加到当前批次
            if len(chunk) >= batch_size:
                # 当批次大小达到1000行时，使用线程池并行处理当前批次
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                    counts = list(executor.map(process_log_chunk, [chunk]))
                    total_count += sum(counts)
                chunk = []
        if chunk:
            # 处理文件末尾可能不足1000行的剩余行
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                counts = list(executor.map(process_log_chunk, [chunk]))
                total_count += sum(counts)

    return total_count


if __name__ == "__main__":
    log_file = 'log_file.log'
    num_threads = 4  # 线程数
    total_count = process_log_file(log_file, num_threads=num_threads)
    print(f"包含domain1.com的总数为: {total_count}")
