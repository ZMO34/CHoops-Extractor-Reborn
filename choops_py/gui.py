import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import subprocess,sys,threading,queue,shlex
from pathlib import Path
from .cli import SPECS,parser
from .archive.manifests import OUTPUT,safe_output
PANELS=[('Build Cache',['build-cache','cache-info','resolve-name']),('Full Rip',['rip']),('Inspect IFF',['inspect-iff']),('Validate IFF',['validate-iff']),('IFF Round Trip',['round-trip-iff']),('Dump IFF Subfiles',['dump-iff-subfiles']),('Replace IFF Subfile',['replace-iff-subfile']),('Inspect/Validate CDF Pair',['inspect-cdf-pair','validate-cdf-pair','round-trip-cdf-pair']),('Dump CDF Pair',['dump-cdf-pair']),('Replace CDF Payload',['replace-cdf-payload']),('Tool Wrapper Tools',['inspect-tool-wrapper','unwrap-tool-file','wrap-tool-file']),('TXTR Inspection',['inspect-txtr','extract-textures']),('Uniform Atlas Inspection',['inspect-uniform-atlas']),('Import Override',['import']),('List/Validate Overrides',['list-overrides','validate-mod']),('Build Copy',['build-copy']),('Validate Build',['validate-build']),('Rip Audit',['audit-rip']),('Roster Detect/Decode/Compare (experimental)',['roster-detect','roster-decode','roster-compare','roster-validate']),('SCNE/Floor Inspector (read only)',['inspect-floor-scne']),('Audio Preservation Tools',['inspect-audo','extract-audio-payloads']),('Logs/Reports Viewer',[])]
COMMAND_REGISTRY={c:SPECS[c] for _,cs in PANELS for c in cs}
class App:
    def __init__(self,root):
        self.root=root;root.title('CHoops Extractor Reborn — Python');root.geometry('1100x800');self.events=queue.Queue();self.process=None
        self.vanilla=tk.StringVar();self.mod=tk.StringVar(value=str(OUTPUT/'builds'/'mods'));self.rip=tk.StringVar(value=str(OUTPUT/'rips'));self.build=tk.StringVar(value=str(OUTPUT/'builds'));self.reports=tk.StringVar(value=str(OUTPUT/'reports'))
        settings=ttk.LabelFrame(root,text='Workspace folders') ;settings.pack(fill='x',padx=8,pady=4)
        for i,(label,var) in enumerate([('Vanilla/JB input',self.vanilla),('Mod folder',self.mod),('Rip output',self.rip),('Build output',self.build),('Reports',self.reports)]):
            ttk.Label(settings,text=label).grid(row=i,column=0,sticky='w');ttk.Entry(settings,textvariable=var,width=100).grid(row=i,column=1,sticky='ew');ttk.Button(settings,text='Browse',command=lambda v=var:self.pick(v,True)).grid(row=i,column=2)
        body=ttk.Frame(root);body.pack(fill='both',expand=True);self.panel_list=tk.Listbox(body,width=38,exportselection=False);self.panel_list.pack(side='left',fill='y')
        for name,_ in PANELS:self.panel_list.insert('end',name)
        self.form=ttk.Frame(body);self.form.pack(side='left',fill='both',expand=True);self.panel_list.bind('<<ListboxSelect>>',self.select_panel)
        self.command=tk.StringVar();self.fields={};self.options=tk.StringVar();self.preview=tk.StringVar()
        ttk.Label(root,textvariable=self.preview,wraplength=1050).pack(fill='x',padx=8)
        actions=ttk.Frame(root);actions.pack(fill='x');self.run_button=ttk.Button(actions,text='Preview and Run',command=self.run);self.run_button.pack(side='left');ttk.Button(actions,text='Save Logs',command=self.save_logs).pack(side='left');ttk.Button(actions,text='Open Report',command=self.open_report).pack(side='left')
        self.logs=tk.Text(root,height=14);self.logs.pack(fill='both',padx=8,pady=4);root.after(100,self.poll);self.panel_list.selection_set(0);self.select_panel()
        root.protocol('WM_DELETE_WINDOW',self.close)
    def pick(self,var,directory=False):
        value=filedialog.askdirectory() if directory else filedialog.askopenfilename()
        if value:var.set(value)
    def select_panel(self,event=None):
        for w in self.form.winfo_children():w.destroy()
        index=self.panel_list.curselection()[0];commands=PANELS[index][1]
        if not commands:
            ttk.Label(self.form,text='Open a report or save the live job logs below.').pack();return
        self.command.set(commands[0]);combo=ttk.Combobox(self.form,textvariable=self.command,values=commands,state='readonly');combo.pack(fill='x');combo.bind('<<ComboboxSelected>>',lambda e:self.build_form());self.fields_frame=ttk.Frame(self.form);self.fields_frame.pack(fill='x');self.build_form()
    def build_form(self):
        for w in self.fields_frame.winfo_children():w.destroy()
        self.fields={};c=self.command.get()
        for i,field in enumerate(SPECS[c]):
            default=''
            if field=='source':default=self.vanilla.get()
            if field=='mod':default=self.mod.get()
            if field=='output':
                base=self.rip.get() if c=='rip' else self.build.get() if c=='build-copy' else self.reports.get()
                default=str(Path(base)/c)
                if c in ('validate-iff','validate-cdf-pair'):default+='.json'
                if c in ('round-trip-iff','replace-iff-subfile'):default+='.iff'
            var=tk.StringVar(value=default);self.fields[field]=var;ttk.Label(self.fields_frame,text=field).grid(row=i,column=0,sticky='w');ttk.Entry(self.fields_frame,textvariable=var,width=75).grid(row=i,column=1,sticky='ew')
            if field not in ('selector','type','value','blocks'):ttk.Button(self.fields_frame,text='Browse',command=lambda v=var,f=field:self.pick(v,f in ('source','mod','modded','rip_output') or f=='output' and c not in ('validate-iff','validate-cdf-pair','round-trip-iff','replace-iff-subfile'))).grid(row=i,column=2)
        self.options.set('--same-size-only' if c.startswith('replace-') else '')
        i=len(self.fields);ttk.Label(self.fields_frame,text='Options').grid(row=i,column=0);ttk.Entry(self.fields_frame,textvariable=self.options,width=75).grid(row=i,column=1)
        ttk.Label(self.fields_frame,text='Options use CLI syntax. Wrapper type is a numeric ID. Roster/TXTR semantic editing is experimental and blocked.',wraplength=650).grid(row=i+1,column=0,columnspan=3)
    def args(self):
        result=[self.command.get()]
        for field,var in self.fields.items():
            value=var.get().strip()
            if value:result.extend(shlex.split(value,posix=False) if field=='blocks' else [value])
        result.extend(shlex.split(self.options.get(),posix=True));return result
    def run(self):
        if self.process:return
        args=self.args();self.preview.set(subprocess.list2cmdline([sys.executable,'-m','choops_py.cli',*args]))
        try:
            a=parser().parse_args(args)
            if hasattr(a,'output'):safe_output(a.output,[self.vanilla.get()] if self.vanilla.get() else [])
            if a.command=='import':safe_output(a.mod,[self.vanilla.get()] if self.vanilla.get() else [])
        except (ValueError,SystemExit) as e:messagebox.showerror('Invalid command',str(e));return
        if not messagebox.askokcancel('Run command',self.preview.get()):return
        self.run_button.config(state='disabled');self.process=True
        def worker():
            try:
                proc=subprocess.Popen([sys.executable,'-u','-m','choops_py.cli',*args],cwd=str(Path(__file__).resolve().parents[1]),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                for line in proc.stdout:self.events.put(line)
                self.events.put(f'Exit code: {proc.wait()}\n')
            except OSError as e:self.events.put(str(e)+'\n')
            finally:self.events.put(None)
        threading.Thread(target=worker,daemon=True).start()
    def poll(self):
        while not self.events.empty():
            line=self.events.get()
            if line is None:self.process=None;self.run_button.config(state='normal')
            else:self.logs.insert('end',line);self.logs.see('end')
        self.root.after(100,self.poll)
    def save_logs(self):
        p=filedialog.asksaveasfilename(initialdir=str(OUTPUT/'reports'),defaultextension='.txt')
        if p:
            try:
                from .archive.manifests import write_bytes
                write_bytes(p,self.logs.get('1.0','end').encode(),[self.vanilla.get()] if self.vanilla.get() else [])
            except ValueError as e:messagebox.showerror('Unsafe output',str(e))
    def open_report(self):
        p=filedialog.askopenfilename(initialdir=self.reports.get())
        if p:
            with Path(p).open(encoding='utf-8',errors='replace') as f:self.logs.insert('end',f.read(2*1024*1024))
    def close(self):
        if self.process:messagebox.showinfo('Job running','Wait for the current job to finish before closing.');return
        self.root.destroy()
def launch():
    root=tk.Tk();App(root);root.mainloop()
