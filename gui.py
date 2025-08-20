import calendar
import datetime
import tkinter as tk
from tkinter import ttk
from holiday_loader import load_year, is_holiday

COLOR_BG = '#FFFFFF'
COLOR_HOLIDAY_BG = '#FFEEEE'
COLOR_MAKEUP_BG = '#E6F3FF'
COLOR_TODAY_BORDER = '#FF6600'
COLOR_WEEKEND_TEXT = '#CC0000'
COLOR_NORMAL_TEXT = '#000000'
COLOR_MAKEUP_TEXT = '#0057B7'

START_YEAR = 2020
END_YEAR = 2035

class CalendarGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('万年历 - 中国节假日')
        self.root.configure(bg=COLOR_BG)
        self.year_var = tk.IntVar(value=datetime.date.today().year)
        self.month_var = tk.IntVar(value=datetime.date.today().month)
        self.holidays_cache = {}
        self.makeup_cache = {}
        self._build_header()
        self._build_legend()
        self.calendar_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.calendar_frame.pack(padx=10, pady=(0,10))
        self.draw_calendar()

    def _build_header(self):
        header = tk.Frame(self.root, bg=COLOR_BG)
        header.pack(padx=10, pady=10, fill='x')
        tk.Label(header, text='年份:', bg=COLOR_BG).pack(side='left')
        year_cb = ttk.Combobox(header, textvariable=self.year_var, width=6,
                    values=[str(y) for y in range(START_YEAR, END_YEAR+1)], state='readonly')
        year_cb.pack(side='left', padx=5)
        year_cb.bind('<<ComboboxSelected>>', lambda e: self.refresh())

        tk.Label(header, text='月份:', bg=COLOR_BG).pack(side='left')
        month_cb = ttk.Combobox(header, textvariable=self.month_var, width=4,
                    values=[str(m) for m in range(1,13)], state='readonly')
        month_cb.pack(side='left', padx=5)
        month_cb.bind('<<ComboboxSelected>>', lambda e: self.refresh())

        tk.Button(header, text='上一月', command=self.prev_month).pack(side='left', padx=5)
        tk.Button(header, text='下一月', command=self.next_month).pack(side='left', padx=5)
        tk.Button(header, text='今天', command=self.goto_today).pack(side='left', padx=5)

    def _build_legend(self):
        legend = tk.Frame(self.root, bg=COLOR_BG)
        legend.pack(padx=10, pady=(0,4), fill='x')
        def box(parent, color, text):
            f = tk.Frame(parent, bg=color, width=16, height=16, highlightthickness=1, highlightbackground='#999')
            f.pack(side='left', padx=4)
            f.pack_propagate(False)
            tk.Label(f, text=' ', bg=color).pack()
            tk.Label(parent, text=text, bg=COLOR_BG).pack(side='left', padx=(0,8))
        box(legend, COLOR_HOLIDAY_BG, '节假日')
        box(legend, COLOR_MAKEUP_BG, '补班日')

    def draw_calendar(self):
        for w in self.calendar_frame.winfo_children():
            w.destroy()
        year = self.year_var.get()
        month = self.month_var.get()
        if year not in self.holidays_cache:
            holidays, makeup = load_year(year)
            self.holidays_cache[year] = holidays
            self.makeup_cache[year] = makeup
        holidays = self.holidays_cache[year]
        makeup = self.makeup_cache[year]
        cal = calendar.Calendar(firstweekday=0)  # Monday=0? Actually 0=Monday in Python docs? No 0=Monday? For Chinese prefer Monday start; Python: 0=Monday.
        # Week headers
        headers = ['一','二','三','四','五','六','日']
        for i, h in enumerate(headers):
            tk.Label(self.calendar_frame, text=h, bg=COLOR_BG, fg=COLOR_NORMAL_TEXT, width=4, font=('Segoe UI', 10, 'bold')).grid(row=0, column=i, padx=2, pady=2)
        first_day = datetime.date(year, month, 1)
        today = datetime.date.today()

        # Adjust calendar to start Monday
        cal = calendar.Calendar(firstweekday=0)
        row = 1
        for week in cal.monthdatescalendar(year, month):
            col = 0
            for d in week:
                if d.month != month:
                    # other month
                    lbl = tk.Label(self.calendar_frame, text=d.day, bg=COLOR_BG, fg='#BBBBBB', width=4)
                    lbl.grid(row=row, column=col, padx=1, pady=1)
                else:
                    status = is_holiday(d, holidays, makeup)
                    bg = COLOR_BG
                    fg = COLOR_NORMAL_TEXT
                    if status == 'holiday':
                        bg = COLOR_HOLIDAY_BG
                        fg = COLOR_WEEKEND_TEXT
                    elif status == 'makeup':
                        bg = COLOR_MAKEUP_BG
                        fg = COLOR_MAKEUP_TEXT
                    else:
                        # weekend coloring
                        if d.weekday() >= 5:
                            fg = COLOR_WEEKEND_TEXT
                    frame = tk.Frame(self.calendar_frame, bg=bg, width=40, height=32, highlightthickness=1)
                    frame.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
                    frame.grid_propagate(False)
                    # Today highlight border
                    if d == today:
                        frame.config(highlightbackground=COLOR_TODAY_BORDER, highlightcolor=COLOR_TODAY_BORDER)
                    else:
                        frame.config(highlightbackground='#CCCCCC')
                    day_lbl = tk.Label(frame, text=str(d.day), bg=bg, fg=fg)
                    day_lbl.pack(anchor='center', expand=True)
                    if status == 'holiday':
                        tip = '节假日'
                    elif status == 'makeup':
                        tip = '补班日'
                    else:
                        tip = None
                    if tip:
                        day_lbl.bind('<Enter>', lambda e, t=tip: self._show_status(t))
                        day_lbl.bind('<Leave>', lambda e: self._show_status(''))
                col += 1
            row += 1
        self.status_var = getattr(self, 'status_var', tk.StringVar())
        if not hasattr(self, 'status_bar'):
            self.status_var.set('')
            self.status_bar = tk.Label(self.root, textvariable=self.status_var, anchor='w', bg=COLOR_BG)
            self.status_bar.pack(fill='x', padx=10, pady=(0,4))

    def _show_status(self, text: str):
        self.status_var.set(text)

    def refresh(self):
        self.draw_calendar()

    def prev_month(self):
        y = self.year_var.get(); m = self.month_var.get()
        m -= 1
        if m == 0:
            m = 12; y -= 1
        self.year_var.set(y); self.month_var.set(m)
        self.refresh()

    def next_month(self):
        y = self.year_var.get(); m = self.month_var.get()
        m += 1
        if m == 13:
            m = 1; y += 1
        self.year_var.set(y); self.month_var.set(m)
        self.refresh()

    def goto_today(self):
        t = datetime.date.today()
        self.year_var.set(t.year); self.month_var.set(t.month)
        self.refresh()


def launch():
    root = tk.Tk()
    CalendarGUI(root)
    root.mainloop()

if __name__ == '__main__':
    launch()
