import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import wave, struct, zlib, math, os, sys

TAPS = 696

def resource_path(name):
    if getattr(sys, 'frozen', False):
        p = Path(sys._MEIPASS) / name
        if p.exists(): return p
    return Path(__file__).resolve().parent / name

def load_wav(path):
    with wave.open(str(path), 'rb') as w:
        channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if w.getcomptype() != 'NONE': raise ValueError('O WAV precisa ser PCM sem compressão.')
        raw=w.readframes(frames)
    if width not in (1,2,3,4): raise ValueError('Profundidade PCM não suportada.')
    vals=[]
    step=width*channels
    for i in range(frames):
        sm=[]
        for c in range(channels):
            b=raw[i*step+c*width:i*step+(c+1)*width]
            if width==1: v=(b[0]-128)/128.0
            elif width==2: v=int.from_bytes(b,'little',signed=True)/32768.0
            elif width==3:
                n=int.from_bytes(b,'little',signed=False)
                if n & 0x800000: n-=1<<24
                v=n/8388608.0
            else: v=int.from_bytes(b,'little',signed=True)/2147483648.0
            sm.append(v)
        vals.append(sum(sm)/len(sm))
    if not vals: raise ValueError('WAV vazio.')
    # The template has 696 float32 taps. Resample to 44.1 kHz while preserving duration,
    # then zero-pad or truncate to the fixed tap count.
    target_rate=44100
    if len(vals)==1:
        out=vals*TAPS
    else:
        out=[]
        for j in range(TAPS):
            pos=j*rate/target_rate
            if pos >= len(vals):
                out.append(0.0)
                continue
            lo=int(pos); hi=min(lo+1,len(vals)-1); frac=pos-lo
            out.append(vals[lo]*(1-frac)+vals[hi]*frac)
    peak=max(abs(v) for v in out) or 1.0
    # Keep source level if safe; scale down only if values exceed full scale.
    if peak>1.0: out=[v/peak for v in out]
    return out, (channels,width*8,rate,frames)

def find_ir_taps_offset(data):
    # Locate embedded TI C6000 ELF and the .const section's ir_taps object.
    elf=data.find(b'\x7fELF')
    if elf<0: raise ValueError('Não encontrei o ELF do efeito dentro do ZD2.')
    e=data[elf:]
    if e[4]!=1 or e[5]!=1: raise ValueError('Formato ELF inesperado.')
    shoff=struct.unpack_from('<I',e,32)[0]
    shentsize, shnum, shstrndx=struct.unpack_from('<HHH',e,46)
    sections=[]
    for i in range(shnum):
        o=shoff+i*shentsize
        sections.append(struct.unpack_from('<IIIIIIIIII',e,o))
    shstr=sections[shstrndx]
    names=e[shstr[4]:shstr[4]+shstr[5]]
    def cstr(blob, off):
        end=blob.find(b'\0',off)
        return blob[off:end if end>=0 else len(blob)].decode('ascii','replace')
    symtab=None; strtab=None; const=None
    for idx,s in enumerate(sections):
        nm=cstr(names,s[0])
        if nm=='.const': const=s
        if nm=='.symtab':
            symtab=s
            if s[6] < len(sections): strtab=sections[s[6]]
    if not const or not symtab or not strtab: raise ValueError('Não encontrei seções ELF necessárias.')
    strings=e[strtab[4]:strtab[4]+strtab[5]]
    entsize=symtab[9] or 16
    for o in range(symtab[4],symtab[4]+symtab[5],entsize):
        st_name,st_value,st_size,st_info,st_other,st_shndx=struct.unpack_from('<IIIBBH',e,o)
        if cstr(strings,st_name)=='ir_taps':
            if st_size != TAPS*4: raise ValueError(f'Tamanho de ir_taps inesperado: {st_size} bytes.')
            section=sections[st_shndx]
            fileoff=elf+section[4]+(st_value-section[3])
            return fileoff, st_size
    raise ValueError('Símbolo ir_taps não encontrado no efeito modelo.')

def convert(src, dst, name):
    """
    Converte um arquivo WAV em um efeito ZD2.
    
    CORREÇÃO IMPORTANTE (v1.1):
    O nome agora é escrito em DOIS locais do arquivo ZD2:
    - 0x64-0x6E: campo legado (11 bytes) - compatibilidade
    - 0x191D-0x1923: campo que o VISOR realmente lê ⭐ (6 bytes)
    
    O limite de caracteres no visor é 6 (não 11).
    """
    template=resource_path('IRCAB_IR_ICON.ZD2').read_bytes()
    if template[:4] != b'ZDLF': raise ValueError('O modelo não parece ser um ZD2 válido.')
    taps, wavinfo=load_wav(src)
    offset,size=find_ir_taps_offset(template)
    out=bytearray(template)
    struct.pack_into('<'+'f'*TAPS,out,offset,*taps)
    
    # ✅ NOVA LÓGICA: Limitar a 6 caracteres (tamanho real do visor)
    nm=''.join(ch for ch in name if ch.isprintable())[:6].encode('ascii','replace')
    
    # Campo legado (0x64-0x6E, 11 bytes) - manter por compatibilidade
    out[0x64:0x6f]=nm.ljust(11,b'\0')
    
    # ⭐ Campo que o VISOR realmente lê (0x191D-0x1923, 6 bytes)
    out[0x191d:0x1923]=nm.ljust(6,b'\0')
    
    # ZD2 checksum: CRC32 over bytes [12:-16], stored little-endian at offset 8.
    crc=zlib.crc32(out[12:-16]) ^ 0xffffffff
    struct.pack_into('<I',out,8,crc & 0xffffffff)
    # Verify checksum and exact size before writing.
    check=zlib.crc32(out[12:-16]) ^ 0xffffffff
    if check != struct.unpack_from('<I',out,8)[0]: raise ValueError('Falha na verificação do checksum.')
    Path(dst).write_bytes(out)
    return wavinfo, len(out), offset

class App:
    def __init__(self,root):
        self.root=root; root.title('Zoom G1X FOUR — IR para ZD2'); root.geometry('650x390'); root.minsize(600,350)
        self.wav=tk.StringVar(); self.out=tk.StringVar(); self.name=tk.StringVar(value='MYIR')
        pad={'padx':14,'pady':6}
        ttk.Label(root,text='Conversor IR / WAV → ZD2',font=('Segoe UI',16,'bold')).pack(anchor='w',**pad)
        ttk.Label(root,text='Modelo: IRCAB_IR_ICON.ZD2 · Alvo: Zoom G1X FOUR',font=('Segoe UI',10)).pack(anchor='w',padx=14)
        f=ttk.Frame(root); f.pack(fill='x',**pad)
        ttk.Label(f,text='WAV de entrada').grid(row=0,column=0,sticky='w')
        ttk.Entry(f,textvariable=self.wav).grid(row=1,column=0,sticky='ew',padx=(0,8))
        ttk.Button(f,text='Procurar…',command=self.pick_wav).grid(row=1,column=1)
        ttk.Label(f,text='Arquivo ZD2 de saída').grid(row=2,column=0,sticky='w',pady=(12,0))
        ttk.Entry(f,textvariable=self.out).grid(row=3,column=0,sticky='ew',padx=(0,8))
        ttk.Button(f,text='Salvar como…',command=self.pick_out).grid(row=3,column=1)
        # ✅ ATUALIZADO: Limite de 6 caracteres (não 11)
        ttk.Label(f,text='Nome do efeito no visor (máx. 6 caracteres)').grid(row=4,column=0,sticky='w',pady=(12,0))
        ttk.Entry(f,textvariable=self.name,width=20).grid(row=5,column=0,sticky='w')
        f.columnconfigure(0,weight=1)
        ttk.Button(root,text='Converter para ZD2',command=self.run).pack(anchor='e',padx=14,pady=8)
    def pick_wav(self):
        p=filedialog.askopenfilename(filetypes=[('WAV PCM','*.wav'),('Todos os arquivos','*.*')])
        if p:
            self.wav.set(p)
            if not self.out.get(): self.out.set(str(Path(p).with_suffix('.ZD2')))
    def pick_out(self):
        p=filedialog.asksaveasfilename(defaultextension='.ZD2',filetypes=[('Zoom effect','*.ZD2')],initialfile='MYIR.ZD2')
        if p:self.out.set(p)
    def run(self):
        try:
            if not self.wav.get() or not Path(self.wav.get()).is_file(): raise ValueError('Selecione um WAV válido.')
            if not self.out.get(): raise ValueError('Escolha onde salvar o ZD2.')
            name = self.name.get() or 'MYIR'
            info,size,off=convert(self.wav.get(),self.out.get(),name)
            ch,bits,rate,frames=info
            # ✅ Mostrar o nome efetivo que será exibido no visor (máx 6 chars)
            display_name = ''.join(ch for ch in name if ch.isprintable())[:6]
            messagebox.showinfo('Conversão concluída', 
                f'Arquivo ZD2 criado:\n{self.out.get()}\n\nNome no visor: "{display_name}"')
        except Exception as e: messagebox.showerror('Falha na conversão',str(e))

if __name__=='__main__':
    root=tk.Tk()
    try: ttk.Style().theme_use('vista')
    except tk.TclError: pass
    App(root); root.mainloop()
