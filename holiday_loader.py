import os
import pandas as pd
import datetime
from ParseJson import get_holidays
from utils.logger import logger

HOLIDAY_DIR = "HolidayData"


def ensure_year_data(year: int):
    """确保某年的 CSV 数据存在；未来年份或获取失败时允许为空返回。

    规则：
    1. 若文件已存在直接使用。
    2. 若 year > 当前年份，认为是未来年份，不主动抓取（官方尚未发布），返回空（文件可能不存在）。
    3. 其它情况尝试联网获取，失败则记录日志，继续返回路径（文件可能不存在）。
    """
    pub_path = os.path.join(HOLIDAY_DIR, f"public_holidays_{year}.csv")
    makeup_path = os.path.join(HOLIDAY_DIR, f"makeup_workdays_{year}.csv")

    if os.path.exists(pub_path) and os.path.exists(makeup_path):
        return pub_path, makeup_path

    current_year = datetime.date.today().year
    if year > current_year or year < 2002:
        logger.info(f"当前无{year} 年数据，使用普通日历显示。")
        return pub_path, makeup_path

    try:
        logger.info(f"{year} 年节假日数据不存在，尝试获取...")
        get_holidays(str(year))
    except Exception as e:
        logger.warning(f"获取 {year} 年节假日数据失败，改为普通日历: {e}")
    return pub_path, makeup_path


def load_year(year: int):
    pub_path, makeup_path = ensure_year_data(year)
    holidays: set[str] = set()
    makeup: set[str] = set()
    if pub_path and os.path.exists(pub_path):
        try:
            df = pd.read_csv(pub_path)
            holidays.update(df['date'].astype(str).tolist())
        except Exception as e:
            logger.error(f"读取假期文件失败 {pub_path}: {e}")
    if makeup_path and os.path.exists(makeup_path):
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
