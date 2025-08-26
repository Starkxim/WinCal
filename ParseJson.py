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

    try:
        logger.info(f"正在从主API获取{year}年节假日数据...")
        response = requests.get(primary_url, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()  # 如果请求失败，抛出HTTPError异常
        data = response.json()
        logger.info("主API获取成功")
    except requests.exceptions.RequestException as e:
        logger.warning(f"主API请求失败: {e}")
        messagebox.showerror(
            "警告！", f"请求中国节假日API失败: {e}。\n尝试使用备用数据源。"
        )
        try:
            logger.info("尝试使用备用API...")
            response = requests.get(backup_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            logger.info("备用API获取成功")
        except requests.exceptions.RequestException as e:
            logger.error(f"备用API请求失败: {e}")
            messagebox.showerror(
                "警告！",
                f"备用数据源请求失败: {e}。\n请检查网络连接并手动获取数据。若仍无数据，可以自行填写节假日及补班数据。",
            )
            raise Exception("获取节假日和补班日期失败，请检查网络连接") from e
        except Exception as e:
            logger.error(f"备用API处理失败: {e}")
            messagebox.showerror(
                "警告！", f"发生意外错误！获取节假日和补班日期失败: {e}。"
            )
            data = {"Years": {year: []}}  # 使用空数据结构继续执行

    if data is None:
        data = {"Years": {year: []}}  # 使用空数据结构继续执行

    public_holidays = []
    makeup_workdays = []

    if "Years" in data:
        for holiday in data["Years"][year]:
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
        for holiday in data["dates"]:
            # Type check to ensure holiday is a dictionary
            if isinstance(holiday, dict):
                date = holiday["date"]
                if holiday["type"] == "public_holiday":
                    public_holidays.append(date)
                elif holiday["type"] == "transfer_workday":
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
