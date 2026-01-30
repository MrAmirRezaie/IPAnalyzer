"""Simple Tkinter GUI for IPAnalyzer (minimal demo)."""
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from ipanalyzer import WHOISAnalyzer
from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer


class IPAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('IPAnalyzer - GUI')
        self._build()

    def _build(self):
        frm = tk.Frame(self.root)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        tk.Label(frm, text='IP Address:').grid(row=0, column=0, sticky='w')
        self.ip_entry = tk.Entry(frm, width=30)
        self.ip_entry.grid(row=0, column=1, sticky='w')

        btn_whois = tk.Button(frm, text='WHOIS', command=self.run_whois)
        btn_whois.grid(row=0, column=2, padx=4)

        btn_geo = tk.Button(frm, text='GeoIP', command=self.run_geoip)
        btn_geo.grid(row=0, column=3, padx=4)

        self.output = ScrolledText(frm, height=20, width=90)
        self.output.grid(row=1, column=0, columnspan=4, pady=8)

    def run_whois(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            return
        analyzer = WHOISAnalyzer()
        try:
            res = analyzer.analyze_ip(ip)
            self.output.insert('end', f"WHOIS for {ip}:\n{res}\n\n")
        except Exception as e:
            self.output.insert('end', f"Error: {e}\n\n")

    def run_geoip(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            return
        analyzer = GeoIPAnalyzer()
        try:
            res = analyzer.analyze(ip)
            self.output.insert('end', f"GeoIP for {ip}:\n{res}\n\n")
        except Exception as e:
            self.output.insert('end', f"Error: {e}\n\n")

    def run(self):
        self.root.mainloop()

def launch():
    app = IPAnalyzerGUI()
    app.run()
