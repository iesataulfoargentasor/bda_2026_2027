"""Narración continua: las escenas siguen las marcas de la voz, sin cortar el audio."""
import asyncio,json,math
from pathlib import Path
import edge_tts
import build_caso_hotel_resumen as base
base.BUILD=base.ROOT/'.venv/arquitectura-clara-video'
base.BUILD.mkdir(parents=True,exist_ok=True)
B=base.BUILD
OUT=base.OUT
NAME='arquitectura-lambda-kappa'
SCENES=json.loads((base.ROOT/'scripts/arquitectura_clara_video.json').read_text(encoding='utf-8'))
NARRATIONS=[s['narration'] for s in SCENES]
base.SCENES=SCENES

def render(s,i):
 im=base.Image.new('RGB',(1280,720),base.BG);d=base.ImageDraw.Draw(im)
 d.rectangle((0,0,1280,8),fill=base.TEAL)
 base.text(d,(44,24),'UT1 · 1.5  /  DEL COBRO DE ANA AL PANEL',18,base.MUTED,bold=True)
 d.text((1235,25),f'{i+1} / {len(SCENES)}',font=base.font(18),fill=base.MUTED,anchor='ra')
 base.text(d,(44,71),s['title'],35,base.INK,1190,True)
 base.text(d,(46,130),s['label'],23,base.TEAL,1180)
 kind=s.get('kind','normal')
 if kind in ('lambda','lambda_update'):
  updated=kind=='lambda_update'
  base.card(d,50,205,480,125,'CAMINO POR LOTES','Histórico: '+('1.100 € (incluye a Ana)' if updated else '1.000 €'),base.TEAL)
  base.card(d,50,375,480,125,'CAMINO RECIENTE','Pendiente: '+('0 € de Ana' if updated else '100 € de Ana'),base.AMBER)
  for y in (267,437):
   d.line((535,y,640,y,640,350,735,350),fill=base.TEAL,width=4)
  base.arrow(d,705,350,35)
  base.card(d,755,270,470,180,'CONSULTA','1.100 € en total',base.TEAL)
 elif kind in ('kappa','kappa_replay'):
  replay=kind=='kappa_replay'
  titles=['EVENTOS GUARDADOS','PROCESAMIENTO','VISTA PARA CONSULTAR']
  bodies=['Cobros identificados, incluido el de Ana.','Volver a leer y aplicar las reglas.' if replay else 'Procesar el nuevo cobro de 100 €.','Vista reconstruida y validada.' if replay else 'De 1.000 € a 1.100 €.']
  for j in range(3):
   base.card(d,45+j*415,235,365,245,titles[j],bodies[j],base.TEAL if j!=1 else base.AMBER)
   if j<2:base.arrow(d,418+j*415,355,29)
 elif kind=='compare':
  base.card(d,50,215,565,280,'LAMBDA','Histórico por lotes + novedades. La consulta combina ambas partes sin duplicar.',base.TEAL)
  base.card(d,665,215,565,280,'KAPPA','Una vía principal de eventos. Para reconstruir vistas, se vuelven a procesar.',base.AMBER)
 else:
  for j,t in enumerate(['ORIGEN','ENTRADA','PREPARACIÓN','CONSULTA']):
   x=45+j*310;active=s['active'] in (-1,j)
   d.rounded_rectangle((x,207,x+265,277),radius=12,fill=base.TEAL if active else '#DFE6E3')
   d.text((x+132,241),t,font=base.font(21,True),fill='white' if active else base.MUTED,anchor='mm')
   if j<3:base.arrow(d,x+276,242,22)
  base.card(d,65,325,1150,170,s['heading'],s['body'])
 base.text(d,(65,528),s['takeaway'],25,base.INK,1160,True)
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
 (B/'capitulos.json').write_text(json.dumps([dict(inicio=round(starts[i],2),titulo=s['title']) for i,s in enumerate(SCENES)],ensure_ascii=False,indent=2),encoding='utf-8')
 concat=[]
 for i,s in enumerate(base.SCENES):
  base.render(s,i).save(B/f'{i:02}.png')
  concat.extend([f"file '{i:02}.png'",f'duration {boundaries[i+1]-boundaries[i]:.3f}'])
 concat.append(f"file '{len(SCENES)-1:02}.png'")
 (B/'imagenes.txt').write_text('\n'.join(concat),encoding='utf-8')
 style='FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=20'
 print('Montando imágenes y subtítulos sobre la narración continua.',flush=True)
 base.run(['-f','concat','-safe','0','-i','imagenes.txt','-i','narracion.mp3','-vf',f"fps=25,subtitles=subtitulos.srt:force_style='{style}'",'-af','loudnorm=I=-18:TP=-1.5:LRA=11,apad','-t',str(end),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/f'{NAME}.mp4')])
 (OUT/f'{NAME}.txt').write_text('ARQUITECTURA: DEL COBRO DE ANA AL PANEL\nVoz sintética: Ximena (español de España). Narración continua.\n\n'+'\n\n'.join(NARRATIONS),encoding='utf-8')
 (OUT/f'{NAME}.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{base.stamp(a,".")} --> {base.stamp(b,".")}\n{t}' for a,b,t in cues)+'\n',encoding='utf-8')
 base.render(SCENES[0],0).save(OUT/f'{NAME}-portada.jpg',quality=92)
 print(f'Completado: {end:.2f} s. {len(words)} palabras, {len(cues)} subtítulos.',flush=True)
if __name__=='__main__':asyncio.run(main())
