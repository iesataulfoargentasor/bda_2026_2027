// Comprobación de lectura de la UT2, apartado 2.6. No inserta ni modifica datos.
// Se ejecuta sobre la base de la conexión; debe contener los JSONL originales.
// No certifica identidad completa de los archivos ni sustituye la explicación.
(() => {
  const r = db.getCollection('reservas');
  const o = db.getCollection('opiniones');
  let pruebas = 0;
  let fallos = 0;
  function igual(nombre, obtenido, esperado) {
    pruebas++;
    const ok = JSON.stringify(obtenido) === JSON.stringify(esperado);
    if (!ok) fallos++;
    print((ok ? 'OK ' : 'ERROR ') + nombre + ': ' + JSON.stringify(obtenido));
    if (!ok) print('  Esperado: ' + JSON.stringify(esperado));
  }
  print('Base comprobada: ' + db.getName());
  igual('Reservas originales', r.countDocuments({}), 15);
  igual('Opiniones originales', o.countDocuments({}), 6);
  igual('Fechas BSON', r.countDocuments({checkin: {$type: 'date'}}), 15);
  igual('Noches numéricas', r.countDocuments({noches: {$type: 'number'}}), 15);
  igual('Laredo', r.countDocuments({hotel: 'Laredo'}), 3);
  igual('Web', r.countDocuments({canal: 'web'}), 6);
  igual('Laredo web', r.countDocuments({hotel: 'Laredo', canal: 'web'}), 1);
  igual('Laredo no web', r.countDocuments({hotel: 'Laredo', canal: {$ne: 'web'}}), 2);
  igual('Menos de tres noches', r.countDocuments({noches: {$lt: 3}}), 7);
  igual('Importe entre 100 y 200 inclusive', r.countDocuments({importe: {$gte: 100, $lte: 200}}), 6);
  igual('Laredo, Noja o Comillas', r.countDocuments({hotel: {$in: ['Laredo','Noja','Comillas']}}), 7);
  igual('Con extras', r.countDocuments({extras: {$exists: true}}), 6);
  igual('Sin huespedes', r.countDocuments({huespedes: {$exists: false}}), 13);
  igual('Canales Trasmiera', r.distinct('canal',{comarca:'Trasmiera'}).sort(), ['ota','recepcion','web']);
  igual('Cinco importes mayores', r.find({}, {_id:0,hotel:1,importe:1}).sort({importe:-1,_id:1}).limit(5).toArray().map(x=>[x.hotel,x.importe]), [['Potes',490],['Santander',410],['Laredo',372],['Potes',280],['Reinosa',260]]);
  igual('NOR', r.countDocuments({noches:{$lte:2},$nor:[{canal:'ota'},{hotel:'Reinosa'}]}),3);
  igual('Importe al menos 80 por noche',r.countDocuments({$expr:{$gte:['$importe',{$multiply:['$noches',80]}]}}),2);
  igual('Web, puestos 5 a 8',r.find({canal:'web'}).sort({importe:-1,_id:1}).skip(4).limit(4).toArray().map(x=>[x.hotel,x.importe]),[['Reinosa',140],['Comillas',89.9]]);
  igual('Abril UTC',r.countDocuments({checkin:{$gte:ISODate('2026-04-01T00:00:00Z'),$lt:ISODate('2026-05-01T00:00:00Z')}}),3);
  igual('Playa',o.countDocuments({etiquetas:'playa'}),3);
  igual('Playa y parking',o.countDocuments({etiquetas:{$all:['playa','parking']}}),1);
  igual('Playa o nieve',o.countDocuments({etiquetas:{$in:['playa','nieve']}}),4);
  igual('Sin spa',o.countDocuments({etiquetas:{$nin:['spa']}}),5);
  igual('Un comentario',o.countDocuments({comentarios:{$size:1}}),3);
  igual('Al menos un comentario',o.countDocuments({'comentarios.0':{$exists:true}}),5);
  igual('Comentarios de Luis',o.countDocuments({'comentarios.autor':'Luis Sainz'}),2);
  const proyeccion=o.find({'comentarios.autor':'Luis Sainz'},{_id:0,titulo:1,comentarios:{$elemMatch:{autor:'Luis Sainz'}}}).toArray();
  igual('Primer comentario coincidente',proyeccion.length===2 && proyeccion.every(x=>x.comentarios.length===1 && x.comentarios[0].autor==='Luis Sainz'),true);
  igual('Wifi en cuerpo principal',o.find({cuerpo:/wifi/i},{_id:0,titulo:1}).toArray().map(x=>x.titulo),['Spa y wifi']);
  const recorte=o.findOne({titulo:'Centro y ruido'},{_id:0,titulo:1,comentarios:{$slice:2},etiquetas:{$slice:3}});
  igual('Recorte de arrays',recorte ? [recorte.comentarios.length,recorte.etiquetas.length] : null,[2,3]);
  const campos=r.find({hotel:'Laredo'},{_id:0,hotel:1,importe:1}).toArray();
  igual('Proyección hotel e importe',campos.length===3 && campos.every(x=>Object.keys(x).sort().join(',')==='hotel,importe'),true);
  print('Pruebas: '+pruebas+'; fallos: '+fallos);
  if (fallos) throw new Error('Revisad base, importación y modificaciones previas. No se ha cambiado ningún dato.');
})();
