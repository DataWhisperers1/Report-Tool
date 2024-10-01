import json
import csv
import smtplib
import os
import requests
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ReportToolGUI:
    def __init__(self, master, filename='reports.json', email_config=None, backup_dir='backups'):
        self.master = master
        master.title("Report Tool")
        master.geometry('800x600')  # تحسين حجم النافذة
        self.filename = filename
        self.email_config = email_config
        self.reports = self.load_reports()
        self.backup_dir = backup_dir
        self.ensure_backup_directory()
        self.language = 'ar'  # افتراضيًا، اللغة هي العربية

        # إعداد القوائم المنسدلة للتحكم في اللغات
        self.language_menu = tk.Menu(master)
        self.language_menu.add_command(label="العربية", command=lambda: self.set_language('ar'))
        self.language_menu.add_command(label="English", command=lambda: self.set_language('en'))
        master.config(menu=self.language_menu)

        # إنشاء الواجهة الرسومية
        self.create_widgets()
        self.update_language()

    def create_widgets(self):
        """إنشاء عناصر الواجهة الرسومية"""
        self.label = ttk.Label(self.master, text="أداة التقارير", font=("Arial", 16))
        self.label.pack(pady=10)

        # الحقول لإدخال اسم المستخدم والنشاط
        self.username_label = ttk.Label(self.master, text="اسم المستخدم:")
        self.username_label.pack()
        self.username_entry = ttk.Entry(self.master)
        self.username_entry.pack()

        self.activity_label = ttk.Label(self.master, text="النشاط:")
        self.activity_label.pack()
        self.activity_entry = ttk.Entry(self.master)
        self.activity_entry.pack()

        # الحقل لإدخال ملف البروكسيات
        self.proxy_label = ttk.Label(self.master, text="ملف البروكسيات (اختياري):")
        self.proxy_label.pack()
        self.proxy_entry = ttk.Entry(self.master)
        self.proxy_entry.pack()
        self.browse_button = ttk.Button(self.master, text="تصفح", command=self.load_proxy_file)
        self.browse_button.pack()

        # زر لإضافة التقرير
        self.add_report_button = ttk.Button(self.master, text="إضافة تقرير", command=self.add_report)
        self.add_report_button.pack(pady=10)

        # زر لعرض التقارير
        self.display_reports_button = ttk.Button(self.master, text="عرض التقارير", command=self.display_reports)
        self.display_reports_button.pack()

        # زر لتحليل التقارير
        self.analyze_reports_button = ttk.Button(self.master, text="تحليل التقارير", command=self.analyze_reports)
        self.analyze_reports_button.pack()

        # زر لتصدير التقارير
        self.export_reports_button = ttk.Button(self.master, text="تصدير التقارير", command=self.export_reports)
        self.export_reports_button.pack(pady=10)

        # قائمة لعرض التقارير
        self.report_list = tk.Listbox(self.master, width=100, height=10)
        self.report_list.pack(pady=10)

        # إعدادات البريد الإلكتروني (إن وجدت)
        self.email_alert_button = ttk.Button(self.master, text="إعداد البريد الإلكتروني", command=self.configure_email)
        self.email_alert_button.pack(pady=10)

        # زر للتحقق من البروكسيات
        self.check_proxies_button = ttk.Button(self.master, text="التحقق من البروكسيات", command=self.check_proxies)
        self.check_proxies_button.pack(pady=10)

        # زر لحفظ واستيراد الإعدادات
        self.save_config_button = ttk.Button(self.master, text="حفظ الإعدادات", command=self.save_config)
        self.save_config_button.pack(pady=10)

        self.load_config_button = ttk.Button(self.master, text="تحميل الإعدادات", command=self.load_config)
        self.load_config_button.pack(pady=10)

        # إضافة شريط تقدم للتحقق من البروكسيات
        self.progress_bar = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=10)
        

    def set_language(self, lang):
        """تغيير اللغة"""
        self.language = lang
        self.update_language()

    def update_language(self):
        """تحديث النصوص بناءً على اللغة المختارة"""
        if self.language == 'ar':
            self.label.config(text="أداة التقارير")
            self.username_label.config(text="اسم المستخدم:")
            self.activity_label.config(text="النشاط:")
            self.proxy_label.config(text="ملف البروكسيات (اختياري):")
            self.add_report_button.config(text="إضافة تقرير")
            self.display_reports_button.config(text="عرض التقارير")
            self.analyze_reports_button.config(text="تحليل التقارير")
            self.export_reports_button.config(text="تصدير التقارير")
            self.email_alert_button.config(text="إعداد البريد الإلكتروني")
            self.check_proxies_button.config(text="التحقق من البروكسيات")
            self.save_config_button.config(text="حفظ الإعدادات")
            self.load_config_button.config(text="تحميل الإعدادات")
        elif self.language == 'en':
            self.label.config(text="Report Tool")
            self.username_label.config(text="Username:")
            self.activity_label.config(text="Activity:")
            self.proxy_label.config(text="Proxy File (Optional):")
            self.add_report_button.config(text="Add Report")
            self.display_reports_button.config(text="Display Reports")
            self.analyze_reports_button.config(text="Analyze Reports")
            self.export_reports_button.config(text="Export Reports")
            self.email_alert_button.config(text="Configure Email")
            self.check_proxies_button.config(text="Check Proxies")
            self.save_config_button.config(text="Save Settings")
            self.load_config_button.config(text="Load Settings")
            

    def load_reports(self):
        """Load reports from a JSON file."""
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_reports(self):
        """Save current reports to a JSON file."""
        self.backup_reports()  # Create a backup before saving new reports
        with open(self.filename, 'w') as file:
            json.dump(self.reports, file, indent=4)

    def ensure_backup_directory(self):
        """Ensure the backup directory exists."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def backup_reports(self):
        """Create a backup of the current reports."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = os.path.join(self.backup_dir, f'reports_backup_{timestamp}.json')
        with open(backup_filename, 'w') as backup_file:
            json.dump(self.reports, backup_file, indent=4)
        print(f"Backup created: {backup_filename}")

    def load_proxy_file(self):
        """Load proxies from an external file."""
        proxy_file = filedialog.askopenfilename(title="اختر ملف البروكسيات", filetypes=[("Text Files", "*.txt")])
        if proxy_file:
            with open(proxy_file, 'r') as file:
                self.proxy_entry.delete(0, tk.END)
                self.proxy_entry.insert(0, proxy_file)
            print(f"Loaded proxies from {proxy_file}")

    def check_proxies(self):
        """Check the validity of proxies in the file."""
        proxy_file = self.proxy_entry.get()
        if not proxy_file:
            messagebox.showerror("خطأ", "يرجى تحديد ملف البروكسيات أولاً.")
            return

        valid_proxies = []
        with open(proxy_file, 'r') as file:
            proxies = file.readlines()

        self.progress_bar['maximum'] = len(proxies)
        print("جارٍ التحقق من صحة البروكسيات...")
        for index, proxy in enumerate(proxies):
            if self.verify_proxy(proxy.strip()):
                valid_proxies.append(proxy.strip())
            self.progress_bar['value'] = index + 1
            self.master.update_idletasks()

        if valid_proxies:
            print(f"تم التحقق من صحة {len(valid_proxies)} بروكسيات.")
            messagebox.showinfo("نجاح", f"تم التحقق من صحة {len(valid_proxies)} بروكسيات.")
        else:
            messagebox.showwarning("تحذير", "لا توجد بروكسيات صالحة.")

    def verify_proxy(self, proxy):
        """Verify the validity of the proxy."""
        try:
            response = requests.get('https://www.google.com', proxies={"http": proxy, "https": proxy}, timeout=3)
            return response.status_code == 200
        except:
            return False

    def add_report(self):
        """Add a new report."""
        username = self.username_entry.get()
        activity = self.activity_entry.get()
        if username and activity:
            timestamp = datetime.now().isoformat()
            report = {"username": username, "activity": activity, "timestamp": timestamp}
            self.reports.append(report)
            self.report_list.insert(tk.END, f"{username} - {activity} - {timestamp}")
            self.username_entry.delete(0, tk.END)
            self.activity_entry.delete(0, tk.END)
            self.save_reports()
            messagebox.showinfo("نجاح", "تم إضافة التقرير بنجاح!")
        else:
            messagebox.showwarning("تحذير", "يرجى ملء جميع الحقول")

    def display_reports(self):
        """Display all reports."""
        self.report_list.delete(0, tk.END)
        if not self.reports:
            self.report_list.insert(tk.END, "لا توجد تقارير بعد.")
            return
        for report in self.reports:
            self.report_list.insert(tk.END, f"{report['username']} - {report['activity']} - {report['timestamp']}")

    def analyze_reports(self):
        """Analyze current reports."""
        activity_count = defaultdict(int)
        user_count = defaultdict(int)

        for report in self.reports:
            activity_count[report['activity']] += 1
            user_count[report['username']] += 1

        analysis = {
            "activity_count": dict(activity_count),
            "user_count": dict(user_count),
            "total_reports": len(self.reports),
        }

        analysis_result = "\n".join([f"{activity}: {count}" for activity, count in activity_count.items()])
        messagebox.showinfo("تحليل التقارير", f"عدد الأنشطة المبلغ عنها: {len(activity_count)}\nعدد المستخدمين المبلغ عنهم: {len(user_count)}\n\nتفاصيل الأنشطة:\n{analysis_result}")

    def export_reports(self):
        """Export reports to CSV and JSON."""
        csv_filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        json_filename = csv_filename.replace(".csv", ".json")

        if csv_filename:
            # Export to CSV
            with open(csv_filename, 'w', newline='') as csvfile:
                fieldnames = ['username', 'activity', 'timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for report in self.reports:
                    writer.writerow(report)

            # Export to JSON
            with open(json_filename, 'w') as jsonfile:
                json.dump(self.reports, jsonfile, indent=4)

            messagebox.showinfo("نجاح", f"تم تصدير التقارير إلى {csv_filename} و {json_filename} بنجاح!")

    def configure_email(self):
        """Configure email settings."""
        config_window = tk.Toplevel(self.master)
        config_window.title("إعداد البريد الإلكتروني")

        tk.Label(config_window, text="بريد المرسل:").pack()
        sender_email_entry = tk.Entry(config_window)
        sender_email_entry.pack()

        tk.Label(config_window, text="كلمة المرور:").pack()
        password_entry = tk.Entry(config_window, show="*")
        password_entry.pack()

        tk.Label(config_window, text="خادم SMTP:").pack()
        smtp_server_entry = tk.Entry(config_window)
        smtp_server_entry.pack()

        tk.Label(config_window, text="منفذ SMTP:").pack()
        smtp_port_entry = tk.Entry(config_window)
        smtp_port_entry.pack()

        def save_email_config():
            """Save email settings."""
            self.email_config = {
                'sender_email': sender_email_entry.get(),
                'password': password_entry.get(),
                'smtp_server': smtp_server_entry.get(),
                'smtp_port': int(smtp_port_entry.get())
            }
            config_window.destroy()
            messagebox.showinfo("نجاح", "تم حفظ إعدادات البريد الإلكتروني بنجاح!")

        tk.Button(config_window, text="حفظ", command=save_email_config).pack(pady=10)

    def send_email_alert(self, subject, body, to_email):
        """Send email alert."""
        if not self.email_config:
            messagebox.showwarning("خطأ", "إعدادات البريد الإلكتروني غير متوفرة.")
            return

        try:
            # إعداد رسالة البريد الإلكتروني
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # الاتصال بخادم SMTP وإرسال البريد الإلكتروني
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['password'])
            server.sendmail(self.email_config['sender_email'], to_email, msg.as_string())
            server.quit()
            print(f"Email sent successfully to {to_email}")
            messagebox.showinfo("نجاح", f"تم إرسال البريد الإلكتروني إلى {to_email} بنجاح!")
        except Exception as e:
            messagebox.showerror("فشل", f"فشل في إرسال البريد الإلكتروني: {e}")

    def save_config(self):
        """Save settings to a config file."""
        config_data = {
            'filename': self.filename,
            'email_config': self.email_config,
            'backup_dir': self.backup_dir,
        }
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        messagebox.showinfo("نجاح", "تم حفظ الإعدادات بنجاح!")

    def load_config(self):
        """Load settings from a config file."""
        try:
            with open('config.json', 'r') as config_file:
                config_data = json.load(config_file)
                self.filename = config_data.get('filename', self.filename)
                self.email_config = config_data.get('email_config', None)
                self.backup_dir = config_data.get('backup_dir', self.backup_dir)
                messagebox.showinfo("نجاح", "تم تحميل الإعدادات بنجاح!")
        except FileNotFoundError:
            messagebox.showwarning("تحذير", "لا توجد إعدادات محفوظة.")

def run_report_tool():
    root = tk.Tk()
    app = ReportToolGUI(root)
    root.mainloop()

# تشغيل الأداة
if __name__ == "__main__":
    run_report_tool()
