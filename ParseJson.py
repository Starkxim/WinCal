import datetime
import os
import pandas as pd
from tkinter import messagebox
import requests
from config import Config
from utils.logger import logger


def get_holidays(year: str):
    """
    获取节假日和补班日期。

    从指定的主要和备份URL获取节假日和补班日期的JSON数据，并将其保存为CSV文件。

    Raises:
        Exception: 如果获取数据失败，则抛出异常。
    """

    primary_url = "https://www.shuyz.com/githubfiles/china-holiday-calender/master/holidayAPI.json"
    backup_url = f"https://unpkg.com/holiday-calendar@1.1.6/data/CN/{year}.json"

    # 分两步：1) 主API；2) 如果主API无该年份或失败 -> 备用API；3) 仍失败 -> 空数据
    data = None
    try:
        logger.info(f"正在从主API获取{year}年节假日数据...")
        response = requests.get(primary_url, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        primary_data = response.json()
        logger.info("主API获取成功")
        # 主API格式: {"Years": {"2023": [ ... ]}}，但有可能不包含请求年份
        if (
            isinstance(primary_data, dict)
            and "Years" in primary_data
            and isinstance(primary_data.get("Years"), dict)
            and year in primary_data.get("Years", {})
        ):
            data = primary_data
        else:
            logger.warning(f"主API数据中不包含 {year} 年，尝试备用API...")
    except requests.exceptions.RequestException as e:
        logger.warning(f"主API请求失败: {e}，尝试备用API...")
    except Exception as e:
        logger.warning(f"主API处理异常: {e}，尝试备用API...")

    if data is None:  # 需要尝试备用
        try:
            logger.info("正在从备用API获取节假日数据...")
            response = requests.get(backup_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            backup_data = response.json()
            logger.info("备用API获取成功")
            data = backup_data
        except requests.exceptions.RequestException as e:
            logger.error(f"备用API请求失败: {e}")
            # 不再弹多个窗口，合并提示
            messagebox.showerror(
                "警告！",
                f"无法获取 {year} 年节假日数据（主/备接口都失败或缺少年份）。\n错误: {e}\n将生成空文件，可手动编辑。",
            )
            data = {"Years": {year: []}}
        except Exception as e:
            logger.error(f"备用API处理失败: {e}")
            messagebox.showerror(
                "警告！",
                f"备用数据源处理异常: {e}\n将生成空文件，可手动编辑。",
            )
            data = {"Years": {year: []}}

    if data is None:
        data = {"Years": {year: []}}  # 使用空数据结构继续执行

    public_holidays = []
    makeup_workdays = []

    if "Years" in data and isinstance(data.get("Years"), dict) and year in data.get("Years", {}):
        for holiday in data["Years"].get(year, []):
            start_date = holiday["StartDate"]
            end_date = holiday["EndDate"]
            comp_days = holiday["CompDays"]

            # 添加放假日期
            current_date = start_date
            while current_date <= end_date:
                public_holidays.append(current_date)
                current_date = str(pd.to_datetime(current_date) + pd.Timedelta(days=1))[
                    :10
                ]

            # 添加补班日期
            makeup_workdays.extend(comp_days)
    else:
        # 备用API格式：{"dates": [{"date":"2024-01-01","type":"public_holiday"}, ...]}
        for holiday in data.get("dates", []):
            if isinstance(holiday, dict):
                date = holiday.get("date")
                h_type = holiday.get("type")
                if h_type == "public_holiday":
                    public_holidays.append(date)
                elif h_type == "transfer_workday":
                    makeup_workdays.append(date)

    holidays_df = pd.DataFrame(public_holidays, columns=["date"])
    makeup_workdays_df = pd.DataFrame(makeup_workdays, columns=["date"])

    if not os.path.exists("HolidayData"):
        os.makedirs("HolidayData")
    holidays_df.to_csv(
        f"HolidayData/public_holidays_{year}.csv", index=False, encoding="utf-8"
    )
    makeup_workdays_df.to_csv(
        f"HolidayData/makeup_workdays_{year}.csv", index=False, encoding="utf-8"
    )
