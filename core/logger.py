import logging

def setup_logger(log_file="debug.log"):
    # Since curses hijacks stdout, we must log to a file.
    logger = logging.getLogger("dungeon_crawler")
    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    return logger

log = setup_logger()
