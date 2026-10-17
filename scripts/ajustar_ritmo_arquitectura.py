"""Acorta silencios detectados en la narración y reajusta escenas y subtítulos."""
import sys,json,re,subprocess,wave
from pathlib import Path
import build_arquitectura_clara_video as source
base=source.base
ORIGINAL=base.ROOT/'.venv/arquitectura-clara-video'
BUILD=base.ROOT/'.venv/arquitectura-ritmo-video';BUILD.mkdir(parents=True,exist_ok=True)
base.BUILD=BUILD
OUT=base.OUT;NAME='arquitectura-lambda-kappa-ritmo'
FF=base.FF

def command(args):
 r=subprocess.run([FF,'-y',*args],capture_output=True,text=True,encoding='utf-8',errors='replace')
 if r.returncode:raise RuntimeError(r.stderr[-4000:])
 return r

command(['-i',str(ORIGINAL/'narracion.mp3'),'-ac','1','-ar','24000','-c:a','pcm_s16le',str(BUILD/'original.wav')])
r=command(['-i',str(BUILD/'original.wav'),'-af','silencedetect=noise=-40dB:d=0.70','-f','null','-'])
spans=[];start=None
for line in r.stderr.splitlines():
 a=re.search(r'silence_start: ([\d.]+)',line)
 b=re.search(r'silence_end: ([\d.]+)',line)
 if a:start=float(a[1])
 if b and start is not None:spans.append((start,float(b[1])));start=None
with wave.open(str(BUILD/'original.wav'),'rb') as w:
 params=w.getparams();raw=w.readframes(w.getnframes());sr=w.getframerate();duration=w.getnframes()/sr
chapters=json.loads((ORIGINAL/'capitulos.json').read_text(encoding='utf-8'))
events=json.loads((ORIGINAL/'marcas.json').read_text(encoding='utf-8'))
cuts=[];kinds={}
for a,b in spans:
 mid=(a+b)/2
 previous=[e for e in events if e['offset']/1e7<mid]
 word=previous[-1]['text'] if previous else ''
 scene=any(a-.15<=c['inicio']<=b+.15 for c in chapters[1:])
 kind='escena' if scene else ('frase' if word.endswith(('.', '?', '!')) else 'interior')
 keep=.62 if scene else (.44 if kind=='frase' else .26)
 if b>=duration-.03:keep=.35;kind='final'
 if b-a<=keep:continue
 left=a+keep/2;right=b-keep/2
 l=round(left*sr);rr=round(right*sr)
 cuts.append((l/sr,rr/sr));kinds[kind]=kinds.get(kind,0)+1
# Solo se eliminan intervalos centrales de silencios, sin acelerar la voz.
parts=[];cursor=0
for a,b in cuts:
 ia=round(a*sr)*2;ib=round(b*sr)*2
 parts.append(raw[cursor:ia]);cursor=ib
parts.append(raw[cursor:]);newraw=b''.join(parts)
with wave.open(str(BUILD/'narracion.wav'),'wb') as w:w.setparams(params);w.writeframes(newraw)
def remap(t):
 return t-sum(max(0,min(t,b)-a) for a,b in cuts if t>a)
new_events=[]
for e in events:
 a=e['offset']/1e7;b=(e['offset']+e['duration'])/1e7
 na,nb=remap(a),remap(b)
 assert nb>na,(e,na,nb)
 new_events.append(dict(e,offset=round(na*1e7),duration=round((nb-na)*1e7)))
assert len(new_events)==1415
cues=base.captions(new_events)
base.write_srt(cues,BUILD/'subtitulos.srt');base.write_srt(cues,OUT/f'{NAME}.es.srt')
newchapters=[dict(c,inicio=round(remap(c['inicio']),4)) for c in chapters]
end=len(newraw)/2/sr+.15
bounds=[c['inicio'] for c in newchapters]+[end]
concat=[]
for i in range(len(source.SCENES)):
 concat.extend([f"file '{(ORIGINAL/f'{i:02}.png').as_posix()}'",f'duration {bounds[i+1]-bounds[i]:.4f}'])
concat.append(f"file '{(ORIGINAL/f'{len(source.SCENES)-1:02}.png').as_posix()}'")
(BUILD/'imagenes.txt').write_text('\n'.join(concat),encoding='utf-8')
(BUILD/'ajustes.json').write_text(json.dumps(dict(cortes=cuts,tipos=kinds,duracion_original=duration,duracion_nueva=end,capitulos=newchapters),ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Pausas ajustadas: {len(cuts)}, por tipo: {kinds}. Duracion: {end:.2f} s. Inicio Lambda/Kappa: {newchapters[10]["inicio"]:.2f} s.',flush=True)
style='FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=20'
base.run(['-f','concat','-safe','0','-i','imagenes.txt','-i','narracion.wav','-vf',f"fps=25,subtitles=subtitulos.srt:force_style='{style}'",'-af','loudnorm=I=-18:TP=-1.5:LRA=11,apad','-t',str(end),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/f'{NAME}.mp4')])
(OUT/f'{NAME}.es.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{base.stamp(a,".")} --> {base.stamp(b,".")}\n{t}' for a,b,t in cues)+'\n',encoding='utf-8')
(OUT/f'{NAME}.txt').write_text((OUT/'arquitectura-lambda-kappa.txt').read_text(encoding='utf-8'),encoding='utf-8')
source.render(source.SCENES[0],0).save(OUT/f'{NAME}-portada.jpg',quality=92)
print('TERMINADO',flush=True)
