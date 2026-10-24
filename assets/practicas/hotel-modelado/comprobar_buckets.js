// Solo lectura. Compara las 120 medidas de la práctica 2.7 con sus dos buckets.
// Ejecutar sobre hotel_modelado después del cálculo guiado.
(() => {
  if(db.getName()!=='hotel_modelado') throw new Error('Conectad a hotel_modelado.');
  function exigir(condicion,texto){if(!condicion)throw new Error(texto);}
  const origen=db.medidas.find().toArray();
  const buckets=db.medidas_hora.find().toArray();
  exigir(origen.length===120,'Se esperaban las 120 medidas originales.');
  exigir(buckets.length===2,'Se esperaban dos buckets.');
  const porId=new Map(origen.map(m=>[m._id,m]));
  const vistos=new Set();
  const horas=new Set();
  for(const b of buckets){
    exigir(b._id.hotel==='Laredo'&&b._id.hab==='214'&&b._id.sensor==='temp-01','Identidad de sensor incorrecta.');
    exigir(b._id.hora instanceof Date,'La hora del bucket debe ser Date.');
    const hora=b._id.hora.toISOString();
    exigir(['2026-04-12T08:00:00.000Z','2026-04-12T09:00:00.000Z'].includes(hora),'Hora inesperada.');
    exigir(!horas.has(hora),'Hora repetida.'); horas.add(hora);
    exigir(Array.isArray(b.medidas)&&b.medidas.length===60,'Cada hora debe conservar 60 medidas.');
    let suma=0;
    for(const m of b.medidas){
      const fuente=porId.get(m.id);
      exigir(fuente!==undefined,'Identificador sin origen: '+m.id);
      exigir(!vistos.has(m.id),'Medida repetida: '+m.id); vistos.add(m.id);
      exigir(m.ts instanceof Date&&fuente.ts instanceof Date,'Instantes sin tipo Date.');
      exigir(m.ts.getTime()===fuente.ts.getTime()&&m.temp_c===fuente.temp_c,'Contenido distinto del origen: '+m.id);
      exigir(fuente.hotel===b._id.hotel&&fuente.hab===b._id.hab&&fuente.sensor===b._id.sensor,'Medida asignada a otro sensor.');
      exigir(Math.floor(m.ts.getTime()/3600000)*3600000===b._id.hora.getTime(),'Medida fuera de su hora.');
      suma+=m.temp_c;
    }
    const esperada=hora.includes('T08:')?1470:1590;
    exigir(suma===esperada&&b.suma===suma,'Suma incorrecta.');
    exigir(b.n===b.medidas.length&&b.temp_media===suma/b.n,'Recuento o media incorrectos.');
  }
  exigir(vistos.size===porId.size,'Faltan identificadores en los buckets.');
  print('CORRECTO: dos buckets, 120 medidas sin pérdidas ni repeticiones; sumas 1470/1590 y medias 24.5/26.5.');
  print('Comprobación de aula sobre datos pequeños; no demuestra rendimiento ni distribución.');
})();
