"""Narración continua: las escenas siguen las marcas de la voz, sin cortar el audio."""
import asyncio,json,math
from pathlib import Path
import edge_tts
import build_caso_hotel_resumen as base
base.BUILD=base.ROOT/'.venv/almacenamiento-ampliado-video'
base.BUILD.mkdir(parents=True,exist_ok=True)
B=base.BUILD
OUT=base.OUT
NAME='almacenamiento-ampliado'
SCENES=json.loads((base.ROOT/'scripts/almacenamiento_ampliado_video.json').read_text(encoding='utf-8'))
NARRATIONS=[s['narration'] for s in SCENES]
base.SCENES=SCENES

def render(s,i):
 im=base.Image.new('RGB',(1280,720),base.BG);d=base.ImageDraw.Draw(im)
 d.rectangle((0,0,1280,8),fill=base.TEAL)
 base.text(d,(44,24),'UT1 · 1.3  /  EL RECORRIDO DE LA RESERVA DE ANA',18,base.MUTED,bold=True)
 d.text((1235,25),f'{i+1} / {len(SCENES)}',font=base.font(18),fill=base.MUTED,anchor='ra')
 base.text(d,(44,71),s['title'],35,base.INK,1190,True)
 base.text(d,(46,130),s['label'],23,base.TEAL,1180)
 for j,t in enumerate(['RECEPCIÓN','ORIGINALES','INFORMES','DEPARTAMENTOS']):
  x=45+j*310;active=s['active'] in (-1,j)
  d.rounded_rectangle((x,207,x+265,277),radius=12,fill=base.TEAL if active else '#DFE6E3')
  d.text((x+132,241),t,font=base.font(21,True),fill='white' if active else base.MUTED,anchor='mm')
  if j<3:base.arrow(d,x+276,242,22)
 base.card(d,65,325,1150,170,s['heading'],s['body'])
 base.text(d,(65,528),s['takeaway'],27,base.INK,1160,True)
 d.rectangle((0,585,1280,720),fill=base.INK)
 d.rectangle((0,714,int(1280*(i+1)/len(SCENES)),719),fill=base.TEAL)
 return im
base.render=render

async def main():
 text=' '.join(NARRATIONS)
 print('Generando una sola narración con Ximena, ritmo +4%.',flush=True)
 events=[]
 with (B/'narracion.mp3').open('wb') as f:
  async for chunk in edge_tts.Communicate(text,'es-ES-XimenaNeural',rate='+4%',boundary='WordBoundary').stream():
   if chunk['type']=='audio':f.write(chunk['data'])
   elif chunk['type']=='WordBoundary':events.append(chunk)
 words=text.split()
 assert len(events)==len(words),(len(events),len(words))
 events=[dict(e,text=w) for e,w in zip(events,words)]
 (B/'marcas.json').write_text(json.dumps(events,ensure_ascii=False),encoding='utf-8')
 cues=base.captions(events)
 base.write_srt(cues,B/'subtitulos.srt')
 base.write_srt(cues,OUT/f'{NAME}.es.srt')
 starts=[0.0];idx=0
 for paragraph in NARRATIONS[:-1]:
  idx+=len(paragraph.split())
  previous=(events[idx-1]['offset']+events[idx-1]['duration'])/1e7
  following=events[idx]['offset']/1e7
  starts.append(round((previous+following)/2,2))
 end=base.duration(B/'narracion.mp3')+.25
 boundaries=starts+[end]
 concat=[]
 for i,s in enumerate(base.SCENES):
  base.render(s,i).save(B/f'{i:02}.png')
  concat.extend([f"file '{i:02}.png'",f'duration {boundaries[i+1]-boundaries[i]:.3f}'])
 concat.append(f"file '{len(SCENES)-1:02}.png'")
 (B/'imagenes.txt').write_text('\n'.join(concat),encoding='utf-8')
 style='FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=20'
 print('Montando imágenes y subtítulos sobre la narración continua.',flush=True)
 base.run(['-f','concat','-safe','0','-i','imagenes.txt','-i','narracion.mp3','-vf',f"fps=25,subtitles=subtitulos.srt:force_style='{style}'",'-af','loudnorm=I=-18:TP=-1.5:LRA=11,apad','-t',str(end),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/f'{NAME}.mp4')])
 (OUT/f'{NAME}.txt').write_text('ALMACENAMIENTO: EL RECORRIDO DE UNA RESERVA\nVoz sintética: Ximena (español de España). Narración continua.\n\n'+'\n\n'.join(NARRATIONS),encoding='utf-8')
 (OUT/f'{NAME}.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{base.stamp(a,".")} --> {base.stamp(b,".")}\n{t}' for a,b,t in cues)+'\n',encoding='utf-8')
 base.render(SCENES[0],0).save(OUT/f'{NAME}-portada.jpg',quality=92)
 print(f'Completado: {end:.2f} s. {len(words)} palabras, {len(cues)} subtítulos.',flush=True)
if __name__=='__main__':asyncio.run(main())
