// Ejecutar con mongosh conectado a hotel_modelado.
// Prepara ejemplos del 2.7; no modifica hotel, hotel_demo ni hotel_escrituras.
// No sobrescribe colecciones existentes: ante un conflicto, termina antes de insertar.
(() => {
  if (db.getName() !== 'hotel_modelado') throw new Error('Conectad a hotel_modelado antes de preparar la práctica.');
  const nombres=['hoteles','reservas_referencias','tarifas','reservas_versionadas','medidas'];
  const existentes=db.getCollectionNames();
  const conflictos=nombres.filter(n=>existentes.includes(n));
  if(conflictos.length) throw new Error('Ya existen colecciones de la práctica: '+conflictos.join(', ')+'. No se ha sobrescrito nada.');
  const hotelId=ObjectId('000000000000000000000027');
  db.hoteles.insertOne({_id:hotelId,nombre:'Laredo',telefono:'942 60 00 00',comarca:'Trasmiera'});
  db.reservas_referencias.insertOne({_id:'R27-1',hotel_id:hotelId,hotel_nombre_historico:'Laredo',canal:'web',noches:Int32(3),importe:186.5});
  db.tarifas.insertOne({_id:'T27-1',hotel:'Laredo',tarifa_web:90,tarifa_ota:110,tarifa_recepcion:100,moneda:'EUR'});
  db.reservas_versionadas.insertMany([
    {_id:'V27-1',hotel:'Laredo',telefono_hotel:'942 60 00 00',noches:Int32(2),importe:124},
    {_id:'V27-2',hotel:{id:hotelId,nombre:'Laredo',telefono:'942 60 00 00'},noches:Int32(3),importe:186.5}
  ]);
  // Dos horas UTC de un único sensor. Valores enteros para comprobar sumas exactas.
  const inicio=Date.UTC(2026,3,12,8,0,0);
  const medidas=[];
  for(let i=0;i<120;i++) medidas.push({
    _id:'M27-'+String(i).padStart(3,'0'),hotel:'Laredo',hab:'214',sensor:'temp-01',
    ts:new Date(inicio+i*60000),temp_c:20+Math.floor(i/60)*2+(i%10)
  });
  // Llegan fuera de orden. _id permite reconocer la misma medida si se reintenta.
  db.medidas.insertMany(medidas.reverse());
  print('Preparado hotel_modelado: 1 hotel, 1 reserva referenciada, 1 tarifa, 2 versiones y 120 medidas.');
  print('UTC 08:00: n=60, suma=1470, media=24.5; UTC 09:00: n=60, suma=1590, media=26.5.');
})();
