// Se ejecuta DENTRO de la red Docker (hostnames rs-laredo, …).
rs.initiate({
  _id: "hotelrs",
  members: [
    { _id: 0, host: "rs-laredo:27017", priority: 2 },
    { _id: 1, host: "rs-potes:27017", priority: 1 },
    { _id: 2, host: "rs-noja:27017", priority: 1 },
  ],
});
