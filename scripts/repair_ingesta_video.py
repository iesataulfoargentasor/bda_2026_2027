"""Repara la locución completa de ETL/ELT y resincroniza el vídeo."""
import asyncio,json,wave,subprocess,shutil
from pathlib import Path
import build_ingesta_video as v
from build_ingesta_video import base,SCENES,NARRATIONS,render,OUT
B=base.ROOT/'.venv/ingesta-historia-corregido'
B.mkdir(parents=True,exist_ok=True)
base.BUILD=B
NAME='ingesta-historia-corregido'
async def main():
 source=base.ROOT/'.venv/ingesta-historia-video'
 events=json.loads((source/'marcas-ajustadas.json').read_text(encoding='utf-8'))
 scene=9
 first=sum(len(t.split()) for t in NARRATIONS[:scene]);last=first+len(NARRATIONS[scene].split())
 chapter=json.loads((source/'capitulos.json').read_text(encoding='utf-8'))
 a=chapter[scene]['inicio'];b=chapter[scene+1]['inicio']
 print('Regenerando el párrafo completo de ETL y ELT.',flush=True)
 spoken=NARRATIONS[scene].replace('para producir una tabla validada. Eso es ELT.', 'para preparar una tabla con los datos ya comprobados. Ese orden corresponde a ELT.')
 marks=[]
 with (B/'reemplazo.mp3').open('wb') as f:
  async for c in v.edge_tts.Communicate(spoken,'es-ES-XimenaNeural',rate='+4%',boundary='WordBoundary').stream():
   if c['type']=='audio':f.write(c['data'])
   elif c['type']=='WordBoundary':marks.append(c)
 assert len(marks)==len(spoken.split())
 marks=[dict(e,text=t) for e,t in zip(marks,spoken.split())]
 # La misma función ajusta solo silencios; aquí las fronteras son las del párrafo.
 shutil.copyfile(B/'reemplazo.mp3',B/'narracion.mp3')
 v.B=B
 v.NARRATIONS=[spoken]
 marks=v.smooth_audio(marks)
 # Corregir la pausa interna de la expresión «una tabla»; conservar sus fonemas.
 r=subprocess.run([base.FF,'-i',str(B/'narracion.wav'),'-af','silencedetect=noise=-40dB:d=0.10','-f','null','-'],capture_output=True,text=True)
 j=next(i for i,e in enumerate(marks) if e['text']=='tabla')
 middle=(marks[j-1]['offset']+marks[j-1]['duration']+marks[j]['offset'])/2e7
 spans=[];begin=None
 for line in r.stderr.splitlines():
  x=v.re.search(r'silence_start: ([\d.]+)',line);y=v.re.search(r'silence_end: ([\d.]+)',line)
  if x:begin=float(x[1])
  if y and begin is not None:spans.append((begin,float(y[1])));begin=None
 lo,hi=next((x,y) for x,y in spans if x<=middle<=y)
 with wave.open(str(B/'narracion.wav'),'rb') as w:
  par=w.getparams();raw=w.readframes(w.getnframes());rate=w.getframerate()
 l=round((lo+.05)*rate);h=round((hi-.05)*rate)
 assert h>l
 samples=v.array.array('h',raw)
 assert max(abs(x) for x in samples[l:h])<330
 with wave.open(str(B/'narracion.wav'),'wb') as w:w.setparams(par);w.writeframes(raw[:l*2]+raw[h*2:])
 def remap(t):return t-max(0,min(t,h/rate)-l/rate)
 marks=[dict(e,offset=round(remap(e['offset']/1e7)*1e7),duration=round((remap((e['offset']+e['duration'])/1e7)-remap(e['offset']/1e7))*1e7)) for e in marks]
 print(f'Pausa interna reducida de {hi-lo:.3f} a 0.100 segundos.',flush=True)
 with wave.open(str(B/'narracion.wav'),'rb') as w:
  replacement=w.readframes(w.getnframes());sr=w.getframerate()
 with wave.open(str(source/'narracion.wav'),'rb') as w:
  params=w.getparams();original=w.readframes(w.getnframes())
 left=round(a*sr);right=round(b*sr)
 duration=len(replacement)/2/sr;delta=duration-(right-left)/sr
 audio=original[:left*2]+replacement+original[right*2:]
 with wave.open(str(B/'narracion.wav'),'wb') as w:w.setparams(params);w.writeframes(audio)
 events=events[:first]+[dict(e,offset=e['offset']+round(left/sr*1e7)) for e in marks]+[dict(e,offset=e['offset']+round(delta*1e7)) for e in events[last:]]
 NARRATIONS[scene]=spoken
 print('Párrafo sustituido; sincronizando escenas y subtítulos.',flush=True)
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
 (OUT/f'{NAME}.txt').write_text('INGESTA: EL VIAJE DE LA RESERVA Y EL COBRO DE ANA\nVoz sintética: Ximena (español de España). Narración continua.\n\n'+'\n\n'.join(NARRATIONS),encoding='utf-8')
 (OUT/f'{NAME}.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{base.stamp(a,".")} --> {base.stamp(b,".")}\n{t}' for a,b,t in cues)+'\n',encoding='utf-8')
 base.render(SCENES[0],0).save(OUT/f'{NAME}-portada.jpg',quality=92)
 print(f'Completado: {end:.2f} s. {len(events)} palabras, {len(cues)} subtítulos.',flush=True)
if __name__=='__main__':asyncio.run(main())
