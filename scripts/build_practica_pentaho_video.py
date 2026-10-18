"""Narración continua: las escenas siguen las marcas de la voz, sin cortar el audio."""
import asyncio,json,math,re,subprocess,wave,array
from pathlib import Path
import edge_tts
import build_caso_hotel_resumen as base
base.BUILD=base.ROOT/'.venv/practica-pentaho-video'
base.BUILD.mkdir(parents=True,exist_ok=True)
B=base.BUILD
OUT=base.OUT
NAME='practica-pentaho'
SCENES=json.loads((base.ROOT/'scripts/practica_pentaho_video.json').read_text(encoding='utf-8'))
NARRATIONS=[s['narration'] for s in SCENES]
base.SCENES=SCENES

def render(s,i):
 im=base.Image.new('RGB',(1280,720),base.BG);d=base.ImageDraw.Draw(im)
 d.rectangle((0,0,1280,8),fill=base.TEAL)
 base.text(d,(44,24),'UT1 / GUÍA DE LA PRÁCTICA INTEGRADORA',18,base.MUTED,bold=True)
 d.text((1235,25),f'{i+1} / {len(SCENES)}',font=base.font(18),fill=base.MUTED,anchor='ra')
 base.text(d,(44,71),s['title'],35,base.INK,1190,True)
 base.text(d,(46,130),s['label'],23,base.TEAL,1180)
 if s.get('kind')=='etl':
  for row,(label,steps) in enumerate([('ETL',['EXTRAER','TRANSFORMAR','CARGAR']),('ELT',['EXTRAER','CARGAR','TRANSFORMAR'])]):
   y=225+row*145
   base.text(d,(50,y+28),label,34,base.TEAL,120,True)
   for j,t in enumerate(steps):
    x=200+j*345
    d.rounded_rectangle((x,y,x+290,y+100),radius=14,fill=base.TEAL if t=='TRANSFORMAR' else '#DFE6E3')
    d.text((x+145,y+50),t,font=base.font(25,True),fill='white' if t=='TRANSFORMAR' else base.INK,anchor='mm')
    if j<3:base.arrow(d,x+300,y+50,30)
 else:
  for j,t in enumerate(['PREPARAR','CONSTRUIR','COMPROBAR','ENTREGAR']):
   x=45+j*310;active=s['active'] in (-1,j)
   d.rounded_rectangle((x,207,x+265,277),radius=12,fill=base.TEAL if active else '#DFE6E3')
   d.text((x+132,241),t,font=base.font(21,True),fill='white' if active else base.MUTED,anchor='mm')
   if j<3:base.arrow(d,x+276,242,22)
   elif j==2:d.ellipse((x+283,239,x+289,245),fill=base.MUTED)
  base.card(d,65,325,1150,170,s['heading'],s['body'])
 base.text(d,(65,528),s['takeaway'],25,base.INK,1160,True)
 d.rectangle((0,585,1280,720),fill=base.INK)
 d.rectangle((0,714,int(1280*(i+1)/len(SCENES)),719),fill=base.TEAL)
 return im
base.render=render

def smooth_audio(events):
 # Conservar respiraciones y pausas de explicación; acortar solo interrupciones mayores de 1,15 s.
 base.run(['-i','narracion.mp3','-ac','1','-ar','24000','-c:a','pcm_s16le','original.wav'])
 r=subprocess.run([base.FF,'-i',str(B/'original.wav'),'-af','silencedetect=noise=-40dB:d=1.15','-f','null','-'],capture_output=True,text=True)
 spans=[];start=None
 for line in r.stderr.splitlines():
  a=re.search(r'silence_start: ([\d.]+)',line);b=re.search(r'silence_end: ([\d.]+)',line)
  if a:start=float(a[1])
  if b and start is not None:spans.append((start,float(b[1])));start=None
 with wave.open(str(B/'original.wav'),'rb') as w:
  params=w.getparams();raw=w.readframes(w.getnframes());sr=w.getframerate();dur=w.getnframes()/sr
 scene_starts=[];idx=0
 for paragraph in NARRATIONS[:-1]:
  idx+=len(paragraph.split());scene_starts.append(((events[idx-1]['offset']+events[idx-1]['duration'])+events[idx]['offset'])/2e7)
 cuts=[]
 for a,b in spans:
  previous=[e for e in events if e['offset']/1e7<(a+b)/2]
  word=previous[-1]['text'] if previous else ''
  keep=.95 if any(a-.15<=t<=b+.15 for t in scene_starts) else (.75 if word.endswith(('.', '?', '!')) else .40)
  if b>=dur-.03:keep=.65
  if b-a>keep:cuts.append((round((a+keep/2)*sr)/sr,round((b-keep/2)*sr)/sr))
 parts=[];cursor=0;samples=array.array('h',raw)
 for a,b in cuts:
  left,right=round(a*sr),round(b*sr)
  assert max(abs(v) for v in samples[left:right])<=330
  parts.append(raw[cursor:left*2]);cursor=right*2
 parts.append(raw[cursor:]);joined=b''.join(parts)
 with wave.open(str(B/'narracion.wav'),'wb') as w:w.setparams(params);w.writeframes(joined)
 def remap(t):return t-sum(max(0,min(t,b)-a) for a,b in cuts if t>a)
 new=[]
 for e in events:
  a,b=remap(e['offset']/1e7),remap((e['offset']+e['duration'])/1e7)
  assert b>a
  new.append(dict(e,offset=round(a*1e7),duration=round((b-a)*1e7)))
 (B/'ajustes.json').write_text(json.dumps(dict(cortes=cuts,duracion_original=dur,duracion_nueva=len(joined)/2/sr),indent=2),encoding='utf-8')
 print(f'Ritmo ajustado: {len(cuts)} silencios; voz conservada sin acelerar.',flush=True)
 return new

async def main():
 text=' '.join(NARRATIONS)
 print('Generando una sola narración con Ximena, ritmo -5%.',flush=True)
 events=[]
 with (B/'narracion.mp3').open('wb') as f:
  async for chunk in edge_tts.Communicate(text,'es-ES-XimenaNeural',rate='-5%',boundary='WordBoundary').stream():
   if chunk['type']=='audio':f.write(chunk['data'])
   elif chunk['type']=='WordBoundary':events.append(chunk)
 words=text.split()
 assert len(events)==len(words),(len(events),len(words))
 events=[dict(e,text=w) for e,w in zip(events,words)]
 (B/'marcas.json').write_text(json.dumps(events,ensure_ascii=False),encoding='utf-8')
 events=smooth_audio(events)
 (B/'marcas-ajustadas.json').write_text(json.dumps(events,ensure_ascii=False),encoding='utf-8')
 cues=base.captions(events)
 base.write_srt(cues,B/'subtitulos.srt')
 base.write_srt(cues,OUT/f'{NAME}.es.srt')
 starts=[0.0];idx=0
 for paragraph in NARRATIONS[:-1]:
  idx+=len(paragraph.split())
  previous=(events[idx-1]['offset']+events[idx-1]['duration'])/1e7
  following=events[idx]['offset']/1e7
  starts.append(round((previous+following)/2,2))
 end=base.duration(B/'narracion.wav')+.15
 boundaries=starts+[end]
 (B/'capitulos.json').write_text(json.dumps([dict(inicio=round(starts[i],2),titulo=s['title']) for i,s in enumerate(SCENES)],ensure_ascii=False,indent=2),encoding='utf-8')
 concat=[]
 for i,s in enumerate(base.SCENES):
  base.render(s,i).save(B/f'{i:02}.png')
  concat.extend([f"file '{i:02}.png'",f'duration {boundaries[i+1]-boundaries[i]:.3f}'])
 concat.append(f"file '{len(SCENES)-1:02}.png'")
 (B/'imagenes.txt').write_text('\n'.join(concat),encoding='utf-8')
 style='FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=20'
 print('Montando imágenes y subtítulos sobre la narración continua.',flush=True)
 base.run(['-f','concat','-safe','0','-i','imagenes.txt','-i','narracion.wav','-vf',f"fps=25,subtitles=subtitulos.srt:force_style='{style}'",'-af','loudnorm=I=-18:TP=-1.5:LRA=11,apad','-t',str(end),'-c:v','libx264','-preset','ultrafast','-tune','stillimage','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/f'{NAME}.mp4')])
 (OUT/f'{NAME}.txt').write_text('PRÁCTICA INTEGRADORA: QUÉ HACER Y QUÉ ENTREGAR\nVoz sintética: Ximena (español de España). Narración continua.\n\n'+'\n\n'.join(NARRATIONS),encoding='utf-8')
 (OUT/f'{NAME}.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{base.stamp(a,".")} --> {base.stamp(b,".")}\n{t}' for a,b,t in cues)+'\n',encoding='utf-8')
 base.render(SCENES[0],0).save(OUT/f'{NAME}-portada.jpg',quality=92)
 print(f'Completado: {end:.2f} s. {len(words)} palabras, {len(cues)} subtítulos.',flush=True)
if __name__=='__main__':asyncio.run(main())
