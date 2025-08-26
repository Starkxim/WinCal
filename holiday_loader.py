import os
import pandas as pd
import datetime
from ParseJson import get_holidays
from utils.logger import logger

HOLIDAY_DIR = "HolidayData"


def ensure_year_data(year: int):
    """确保某年的 CSV 数据存在，不存在则调用接口获取。"""
    pub_path = os.path.join(HOLIDAY_DIR, f"public_holidays_{year}.csv")
    makeup_path = os.path.join(HOLIDAY_DIR, f"makeup_workdays_{year}.csv")
    if not (os.path.exists(pub_path) and os.path.exists(makeup_path)):
        logger.info(f"{year} 年节假日数据不存在，尝试获取...")
        get_holidays(str(year))  # get_holidays 按当前年份获取；若不同则需要适配（后续可扩展）
    return pub_path, makeup_path


def load_year(year: int):
    pub_path, makeup_path = ensure_year_data(year)
    holidays = set()
    makeup = set()
    if os.path.exists(pub_path):
        try:
            df = pd.read_csv(pub_path)
            holidays.update(df['date'].astype(str).tolist())
        except Exception as e:
            logger.error(f"读取假期文件失败 {pub_path}: {e}")
    if os.path.exists(makeup_path):
        try:
            df = pd.read_csv(makeup_path)
            makeup.update(df['date'].astype(str).tolist())
        except Exception as e:
            logger.error(f"读取补班文件失败 {makeup_path}: {e}")
    return holidays, makeup


def is_holiday(date: datetime.date, holidays: set, makeup: set):
    ds = date.strftime('%Y-%m-%d')
    if ds in makeup:
        return 'makeup'
    if ds in holidays:
        return 'holiday'
    return None
