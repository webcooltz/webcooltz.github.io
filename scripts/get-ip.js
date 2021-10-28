// Base
let apiKey = '5d7982a7599c461a9df3048bdf8fe2dd';
$.getJSON('https://api.bigdatacloud.net/data/ip-geolocation?key=' + apiKey, function(data) {
  console.log(JSON.stringify(data, null, 2));
});