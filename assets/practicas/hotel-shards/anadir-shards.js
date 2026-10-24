// En mongos, una vez que los tres replica sets tienen primario.
(() => {
  if(db.hello().msg!=='isdbgrid') throw new Error('Conectad al router mongos, no a un miembro del shard.');
  const admin=db.getSiblingDB('admin');
  function lista(){const r=admin.runCommand({listShards:1});if(!r.ok)throw new Error('No se pudo consultar listShards');return r.shards;}
  print('Shards antes de registrar:'); printjson(lista());
  for(const [nombre,semilla] of [['trasmiera','trasmiera/trasmiera-a:27017'],['liebana','liebana/liebana-a:27017']]){
    const existente=lista().find(s=>s._id===nombre);
    if(existente){
      if(existente.host.split('/')[0]!==nombre)throw new Error('Configuración inesperada de '+nombre);
      print(nombre+' ya está registrado; no se vuelve a añadir.');
    } else {
      const r=sh.addShard(semilla);
      if(!r.ok)throw new Error('No se pudo añadir '+nombre+': '+JSON.stringify(r));
      print('Incorporado '+nombre);
    }
    printjson(lista());
  }
})();
