import logging

logging.basicConfig(
    format='[%(asctime)s]: %(message)s | %(levelname)s on LINE:%(lineno)d in %(filename)s',
    level=logging.INFO,
    encoding='utf-8',
    # filename='logs.log'
)
