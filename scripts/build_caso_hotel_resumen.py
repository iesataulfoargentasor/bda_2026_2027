"""Vídeo del caso hotelero: guion, esquemas propios, voz sintética y subtítulos.
Requisitos: pillow, edge-tts, imageio-ffmpeg. Ejecutar desde el repositorio.
"""
import asyncio, json, math, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts, imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'.venv/caso-hotel-resumen'; BUILD.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'docs/assets/ut1'; OUT.mkdir(parents=True,exist_ok=True)
SCENES=json.loads((ROOT/'scripts/caso_hotel_resumen.json').read_text(encoding='utf-8-sig'))
FF=imageio_ffmpeg.get_ffmpeg_exe(); W,H=1280,720
BG='#F5F2EA'; INK='#142D43'; TEAL='#197F83'; AMBER='#B36C12'; MUTED='#4D6070'
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',n)
def lines(d,t,f,width):
    out=[];line=''
    for word in t.split():
        nxt=(line+' '+word).strip()
        if d.textlength(nxt,font=f)>width and line:out.append(line);line=word
        else:line=nxt
    return out+[line]
def text(d,xy,t,size=28,color=INK,width=1100,bold=False,gap=8):
    x,y=xy;f=font(size,bold)
    for line in lines(d,t,f,width):d.text((x,y),line,font=f,fill=color);y+=size+gap
    return y

def card(d,x,y,w,h,title,body,accent=TEAL,number=None):
    d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill='white',outline='#D7E0DF',width=2)
    d.rounded_rectangle((x,y,x+7,y+h),radius=3,fill=accent)
    ty=y+22
    if number:
        text(d,(x+22,ty),number,38,accent,w-44,True);ty+=57
    ty=text(d,(x+22,ty),title,27,INK,w-44,True)+13
    end=text(d,(x+22,ty),body,23,MUTED,w-44)
    if end>y+h-10:raise ValueError(('card overflow',title,end,y+h))
def arrow(d,x,y,length=38):
    d.line((x,y,x+length,y),fill=TEAL,width=4)
    d.polygon([(x+length,y),(x+length-10,y-7),(x+length-10,y+7)],fill=TEAL)
def hotel(d,x,y,color=TEAL):
    d.rounded_rectangle((x,y,x+70,y+70),radius=7,fill=color)
    for xx in [x+13,x+43]:
        for yy in [y+12,y+31]:d.rectangle((xx,yy,xx+13,yy+10),fill=BG)
    d.rectangle((x+28,y+52,x+43,y+70),fill=BG)
def person(d,x,y,color=TEAL):
    d.ellipse((x-26,y,x+26,y+52),fill=color)
    d.rounded_rectangle((x-43,y+65,x+43,y+160),radius=22,fill=color)

def render(s,i):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,8),fill=TEAL)
    text(d,(44,24),'UT1  /  EL CASO HOTELERO EN POCAS PALABRAS',18,MUTED,bold=True)
    d.text((1235,25),f'{i+1} / {len(SCENES)}',font=font(18),fill=MUTED,anchor='ra')
    text(d,(44,71),s['title'],37,INK,1190,True)
    text(d,(46,130),s['label'],24,TEAL,1180)
    k=s['kind']
    if k=='hotels':
        for n,name in enumerate(['Santander','Laredo','Comillas','Potes']):
            x=95+n*300;hotel(d,x+55,240,TEAL if n<3 else AMBER)
            text(d,(x,337),name,29,INK,265,True)
        text(d,(252,455),'¿Qué necesita saber la directora?',35,INK,1000,True)
    elif k=='question':
        person(d,155,270,AMBER)
        text(d,(74,460),'Directora',27,INK,210,True)
        card(d,310,215,890,140,'Habitaciones ocupadas','¿Qué ocupación tuvo cada hotel?')
        card(d,310,385,890,140,'Dinero cobrado','¿Qué importe se cobró realmente?',AMBER)
    elif k=='pieces':
        card(d,65,225,510,225,'La reserva de Ana','Dónde y cuándo se aloja.',TEAL,'ESTANCIA')
        card(d,700,225,510,225,'El pago de Ana','Si el cobro está confirmado.',AMBER,'COBRO')
        arrow(d,600,335,70)
        text(d,(307,495),'Reservar no significa haber pagado.',32,INK,1000,True)
    elif k=='you':
        for n,(title,body) in enumerate([('Reunir','Copiar los datos que ya existen.'),('Comprobar','Evitar errores y cobros repetidos.'),('Resumir','Mostrar el resultado por hotel.')]):
            card(d,45+n*415,230,365,235,title,body,TEAL,str(n+1))
            if n<2:arrow(d,420+n*415,350,28)
        text(d,(258,515),'Recepción continúa con su trabajo.',28,INK,1000,True)
    elif k=='time':
        card(d,65,215,550,290,'¿Cómo fue AYER?','El cierre del día anterior, disponible cada mañana a las ocho.',TEAL,'Dirección')
        card(d,665,215,550,290,'¿Qué ocurre AHORA?','Un sensor detecta presencia. No decide si la habitación se puede vender.',AMBER,'Sensores')
    else:
        for n,(title,body) in enumerate([('Recepción','Atiende a los clientes.'),('Vosotros','Preparáis información fiable.'),('Dirección','Entiende cómo va el negocio.')]):
            card(d,45+n*415,225,365,245,title,body,TEAL if n<2 else AMBER,str(n+1))
            if n<2:arrow(d,420+n*415,345,28)
        text(d,(315,515),'Información clara, correcta y a tiempo.',28,INK,900,True)
    d.rectangle((0,585,W,H),fill=INK)
    d.rectangle((0,714,int(W*(i+1)/len(SCENES)),719),fill=TEAL)
    return im

def duration(p):
    r=subprocess.run([FF,'-i',str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',r.stderr)
    if not m:raise ValueError(r.stderr)
    return int(m[1])*3600+int(m[2])*60+float(m[3])
def stamp(t,sep=','):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
def captions(events):
    # Repartir cada frase en grupos equilibrados evita palabras sueltas fugaces.
    sentences=[];sentence=[]
    for e in events:
        sentence.append(e)
        if e['text'].endswith(('.', '?', '!')):
            sentences.append(sentence);sentence=[]
    if sentence:sentences.append(sentence)
    groups=[]
    for sentence in sentences:
        count=max(1,math.ceil(len(sentence)/9),math.ceil(len(' '.join(x['text'] for x in sentence))/65))
        for i in range(count):
            group=sentence[round(i*len(sentence)/count):round((i+1)*len(sentence)/count)]
            if group:groups.append(group)
    return [(g[0]['offset']/1e7,(g[-1]['offset']+g[-1]['duration'])/1e7,' '.join(x['text'] for x in g)) for g in groups]
def write_srt(cues,path):
    import textwrap
    path.write_text('\n\n'.join(f'{n+1}\n{stamp(a)} --> {stamp(b)}\n'+ '\n'.join(textwrap.wrap(t,44)) for n,(a,b,t) in enumerate(cues))+'\n',encoding='utf-8')
async def speech(i,s):
    mp3=BUILD/f'{i:02}.mp3';meta=BUILD/f'{i:02}.json'
    if mp3.exists() and meta.exists():return json.loads(meta.read_text(encoding='utf-8'))
    for attempt in range(3):
        try:
            events=[]
            with mp3.open('wb') as f:
                async for chunk in edge_tts.Communicate(s['narration'],'es-ES-ElviraNeural',rate='-3%',boundary='WordBoundary').stream():
                    if chunk['type']=='audio':f.write(chunk['data'])
                    elif chunk['type']=='WordBoundary':events.append(chunk)
            if not events:raise ValueError('Sin marcas de voz')
            meta.write_text(json.dumps(events,ensure_ascii=False),encoding='utf-8');return events
        except Exception:
            if attempt==2:raise
            await asyncio.sleep(2)
def run(args):
    r=subprocess.run([FF,'-y',*args],cwd=BUILD,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError(r.stderr[-5000:])
async def main():
    allcues=[];offset=0;chapters=[]
    for i,s in enumerate(SCENES):
        print(f'{i+1}/{len(SCENES)}: {s["title"]}',flush=True)
        im=render(s,i);im.save(BUILD/f'{i:02}.png')
        events=await speech(i,s)
        words=s['narration'].split()
        if len(words)!=len(events):raise ValueError('Las marcas de voz no coinciden con el guion')
        events=[dict(e,text=w) for e,w in zip(events,words)]
        cues=captions(events);write_srt(cues,BUILD/f'{i:02}.srt')
        dur=math.ceil((duration(BUILD/f'{i:02}.mp3')+0.65)*25)/25
        chapters.append({'inicio':round(offset,2),'duracion':dur,'titulo':s['title']})
        allcues.extend((a+offset,b+offset,t) for a,b,t in cues)
        style='FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=20'
        run(['-loop','1','-framerate','25','-i',f'{i:02}.png','-i',f'{i:02}.mp3','-vf',f"subtitles={i:02}.srt:force_style='{style}'",'-af','apad','-t',str(dur),'-c:v','libx264','-preset','ultrafast','-tune','stillimage','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',f'{i:02}.mp4'])
        offset+=dur
    (BUILD/'concat.txt').write_text('\n'.join(f"file '{i:02}.mp4'" for i in range(len(SCENES))),encoding='utf-8')
    run(['-f','concat','-safe','0','-i','concat.txt','-c','copy','-movflags','+faststart',str(OUT/'caso-hotel-resumen.mp4')])
    write_srt(allcues,OUT/'caso-hotel-resumen.es.srt')
    (OUT/'caso-hotel-resumen.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{stamp(a,".")} --> {stamp(b,".")}\n{t}' for a,b,t in allcues)+'\n',encoding='utf-8')
    (OUT/'caso-hotel-resumen.txt').write_text('EL CASO HOTELERO DE CANTABRIA\nVídeo de apoyo · BDA · IES Ataúlfo Argenta\nNarración con voz sintética en español. Ejemplos ficticios.\nFuente: https://iesataulfoargentasor.github.io/bda_2026_2027/ut1/caso-hotel/\n\n'+'\n\n'.join(stamp(c['inicio'],'.')[:8]+' · '+s['title']+'\n'+s['narration'] for c,s in zip(chapters,SCENES)),encoding='utf-8')
    render(SCENES[0],0).save(OUT/'caso-hotel-resumen-portada.jpg',quality=92)
    (BUILD/'chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'TERMINADO: {offset:.2f} segundos; {(OUT/"caso-hotel-resumen.mp4").stat().st_size/1024/1024:.1f} MiB',flush=True)
if __name__=='__main__':asyncio.run(main())
