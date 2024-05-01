import logging

logging.basicConfig(
       level=logging.INFO,  # 设置日志级别
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
       datefmt='%Y-%m-%d %H:%M:%S'  # 时间格式
   )
logger = logging.getLogger('my_logger')
