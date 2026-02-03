"""Minimal Tkinter GUI to demonstrate WHOIS and GeoIP lookup."""
try:
    import tkinter as tk
    from tkinter import scrolledtext
except Exception:
    tk = None

from ipanalyzer.modules.whois_analyzer import WHOISAnalyzer
from ipanalyzer.modules.geoip_analyzer import GeoIPAnalyzer


class DesktopApp:
    def __init__(self):
        if tk is None:
            raise RuntimeError('Tkinter not available')
        self.whois = WHOISAnalyzer()
        self.geo = GeoIPAnalyzer()
        self.root = tk.Tk()
        self.root.title('IPAnalyzer GUI')
        self._build()

    def _build(self):
        frm = tk.Frame(self.root)
        frm.pack(padx=10, pady=10)
        tk.Label(frm, text='IP or Host').grid(row=0, column=0)
        self.entry = tk.Entry(frm, width=40)
        self.entry.grid(row=0, column=1)
        tk.Button(frm, text='WHOIS', command=self.run_whois).grid(row=0, column=2, padx=5)
        tk.Button(frm, text='GeoIP', command=self.run_geo).grid(row=0, column=3)

        self.out = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.out.pack(padx=10, pady=10)

    def run_whois(self):
        q = self.entry.get().strip()
        if not q:
            return
        res = self.whois.lookup(q)
        self.out.delete('1.0', 'end')
        self.out.insert('1.0', res.get('raw') if isinstance(res.get('raw'), str) else str(res))

    def run_geo(self):
        q = self.entry.get().strip()
        if not q:
            return
        res = self.geo.lookup(q)
        self.out.delete('1.0', 'end')
        self.out.insert('1.0', str(res))

    def run(self):
        self.root.mainloop()


def main():
    app = DesktopApp()
    app.run()

if __name__ == '__main__':
    main()
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
