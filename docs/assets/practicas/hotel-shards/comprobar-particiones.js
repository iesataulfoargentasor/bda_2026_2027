// Solo lectura; ejecutar en el mongos del laboratorio, base hotel.
// Contrasta contenido completo, identificadores, tipos y noches por hotel.
(() => {
  if(db.hello().msg!=='isdbgrid')throw new Error('Se requiere una conexión a mongos.');
  if(db.getName()!=='hotel')throw new Error('Seleccionad la base hotel de este laboratorio.');
  function canon(v){
    if(Array.isArray(v))return v.map(canon);
    if(v!==null&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,canon(v[k])]));
    return v;
  }
  function documentos(nombre){return db.getCollection(nombre).find().toArray().map(d=>JSON.stringify(canon(EJSON.serialize(d,{relaxed:false})))).sort();}
  // El cliente puede representar int y double como Number. Pedimos los tipos
  // de los campos principales al servidor antes de comparar, sin inferirlos.
  function tipos(nombre){
    return db.getCollection(nombre).aggregate([{$project:{
      campos:{$map:{input:{$objectToArray:'$$ROOT'},as:'campo',in:{campo:'$$campo.k',tipo:{$type:'$$campo.v'}}}}
    }}]).toArray().map(d=>JSON.stringify({id:EJSON.serialize(d._id,{relaxed:false}),campos:d.campos.sort((a,b)=>a.campo.localeCompare(b.campo))})).sort();
  }
  const tiposOriginal=tipos('reservas');
  const original=documentos('reservas');
  if(original.length!==15)throw new Error('La referencia debe contener las 15 reservas originales.');
  const esperado=[['Comillas',4],['Laredo',11],['Noja',4],['Potes',13],['Reinosa',6],['Santander',8]];
  for(const nombre of ['reservas','reservas_rango','reservas_hash']){
    const actual=documentos(nombre);
    if(JSON.stringify(actual)!==JSON.stringify(original))throw new Error('Contenido diferente en '+nombre);
    if(JSON.stringify(tipos(nombre))!==JSON.stringify(tiposOriginal))throw new Error('Tipos BSON distintos en '+nombre);
    const totales=db.getCollection(nombre).aggregate([{$group:{_id:'$hotel',noches:{$sum:'$noches'}}},{$sort:{_id:1}}]).toArray().map(d=>[d._id,d.noches]);
    if(JSON.stringify(totales)!==JSON.stringify(esperado))throw new Error('Noches por hotel incorrectas en '+nombre);
    print('OK '+nombre+': 15 documentos, contenido y tipos principales iguales, 46 noches.');
  }
  print('Conservación verificada. La ubicación se comprueba aparte con sh.status(); esto no demuestra aceleración.');
})();
