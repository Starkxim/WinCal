# WinCal 万年历

一个使用 Tkinter 编写的中国万年历 GUI：

* 按月显示日历
* 支持选择年份与月份（2020-2035 可扩展）
* 自动获取/缓存中国法定节假日与补班日（本地 CSV）
* 不同底色/文字颜色区分：节假日、补班日、周末、今天

## 运行

确保已安装依赖（使用 uv）：

```
uv sync
```

启动：

```
uv run python -m main   # 推荐，自动使用本项目虚拟环境
```

或直接：

```
uv run python main.py
```

首次运行会尝试下载当年节假日数据写入 `HolidayData/` 目录。

注意：若直接运行 `python main.py` 遇到 `ModuleNotFoundError: No module named 'pandas'`，说明未使用项目虚拟环境。请使用 `uv run` 前缀或激活 `.venv`。

## 颜色图例

| 类型 | 背景 | 前景 |
|------|------|------|
| 节假日 | #FFEEEE | 红色 |
| 补班日 | #E6F3FF | 蓝色 |
| 普通周末 | 白底 | 红色 |
| 工作日 | 白底 | 黑色 |
| 今天 | 橙色描边 | - |

## 目录结构

```
main.py                 # 启动入口
gui.py                  # GUI 主界面
ParseJson.py            # 获取节假日 JSON 并生成 CSV
holiday_loader.py       # 读取/缓存节假日数据
config.py               # 配置项
utils/logger.py         # 简单日志
HolidayData/            # 本地生成的 CSV
```

## 扩展方向

* 支持指定任意年份获取（修改 `get_holidays` 逻辑）
* 增加节假日名称悬浮提示
* 导出整年日历为图片或 PDF
* 深色主题 / 自定义主题

## 许可证

MIT（可根据需要调整）。

