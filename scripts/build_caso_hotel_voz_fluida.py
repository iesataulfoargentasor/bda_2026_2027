"""Narración continua: las escenas siguen las marcas de la voz, sin cortar el audio."""
import asyncio,json,math
from pathlib import Path
import edge_tts
import build_caso_hotel_resumen as base
base.BUILD=base.ROOT/'.venv/caso-hotel-voz-fluida'
base.BUILD.mkdir(parents=True,exist_ok=True)
B=base.BUILD
OUT=base.OUT
NAME='caso-hotel-resumen-voz-fluida'
NARRATIONS=[
'Imaginad que empezáis a trabajar para un pequeño grupo de hoteles de Cantabria. Hay uno en Santander, otro en Laredo, otro en Comillas y otro en Potes. Cada uno tiene su ritmo, pero la directora se hace una pregunta muy sencilla: ¿cómo nos fue ayer?',
'Veámoslo con una mañana cualquiera. En recepción están atendiendo a los huéspedes, y la directora quiere saber dos cosas: cuántas habitaciones estuvieron ocupadas y cuánto dinero se cobró en cada hotel. Lo que necesita es tenerlo todo claro, en una sola pantalla.',
'¿Dónde está la dificultad? En que las piezas están repartidas. Mirad el caso de Ana: reserva una habitación en Laredo. Un programa guarda su estancia y otro confirma el pago. Hay que reunir ambas cosas, porque tener una reserva no significa que ya se haya cobrado.',
'¡Y aquí entráis vosotros! Recogéis una copia de esos datos, comprobáis que estén bien y preparáis el resumen por hotel. Por ejemplo, si un cobro aparece repetido, lo contáis una sola vez. Así, la directora puede fiarse del resultado, mientras recepción sigue trabajando con normalidad.',
'Ahora bien, hay un detalle importante: el informe de las ocho de la mañana cuenta cómo terminó el día anterior. Para saber qué pasa ahora tenemos otras señales, como los sensores de presencia. Pero ojo: si Ana sale a desayunar, su habitación sigue reservada. Un dato necesita contexto para entenderlo bien.',
'Y esa es la idea que nos acompañará durante el curso. Recepción atiende a los clientes; la directora necesita entender cómo va el negocio; y vosotros conectáis las piezas. Las herramientas las iremos aprendiendo. De momento, quedaos con el objetivo: convertir datos repartidos en información clara, fiable y a tiempo.'
]
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
 concat.append("file '05.png'")
 (B/'imagenes.txt').write_text('\n'.join(concat),encoding='utf-8')
 style='FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=20'
 print('Montando imágenes y subtítulos sobre la narración continua.',flush=True)
 base.run(['-f','concat','-safe','0','-i','imagenes.txt','-i','narracion.mp3','-vf',f"fps=25,subtitles=subtitulos.srt:force_style='{style}'",'-af','loudnorm=I=-18:TP=-1.5:LRA=11,apad','-t',str(end),'-c:v','libx264','-preset','fast','-tune','stillimage','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/f'{NAME}.mp4')])
 (OUT/f'{NAME}.txt').write_text('EL CASO HOTELERO EN POCAS PALABRAS\nVoz sintética: Ximena (español de España). Narración continua.\n\n'+'\n\n'.join(NARRATIONS),encoding='utf-8')
 (OUT/f'{NAME}.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{base.stamp(a,".")} --> {base.stamp(b,".")}\n{t}' for a,b,t in cues)+'\n',encoding='utf-8')
 print(f'Completado: {end:.2f} s. {len(words)} palabras, {len(cues)} subtítulos.',flush=True)
if __name__=='__main__':asyncio.run(main())
