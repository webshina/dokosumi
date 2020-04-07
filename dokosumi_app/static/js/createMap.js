// 地図を作成する
var mymap = L.map('map');
 
// タイルレイヤーを作成し、地図にセットする
L.tileLayer('http://tile.openstreetmap.jp/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
}).addTo(mymap);
 
// 地図の中心座標とズームレベルを設定する
var lat = document.getElementById('lat').innerText
var lon = document.getElementById('lon').innerText
mymap.setView([lat, lon], 11)

// マーカーを作成する
var marker = L.marker([lat, lon]).addTo(mymap);
 
// クリックした際にポップアップメッセージを表示する
var station_name = document.getElementById('station_name').innerText
marker.bindPopup(station_name);

mymap.invalidateSize