rs.initiate({
  _id: "cfgrs",
  configsvr: true,
  members: [{ _id: 0, host: "cfg-santander:27017" }],
});
