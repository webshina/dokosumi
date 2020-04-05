// rangeバー
var elems = document.getElementsByClassName('valueRange');

for(let i = 0; i < elems.length; i++){
    elemRange = elems[i].getElementsByClassName('range')[0]
    elemRange.addEventListener('input', function(event) {
        var newValue = event.target.value;
        var value = elems[i].getElementsByClassName('value')[0];
        value.innerHTML = newValue;
        var name = event.target.name;
        var description = elems[i].getElementsByClassName('descripion')[0];
        if (newValue >= 0 && newValue < 33) {
            description.innerHTML = "気にしない"
        } else if(newValue >= 33 && newValue < 66) {
            description.innerHTML = "気にする"
        } else {
            description.innerHTML = "重要"
        }
    }, false);
};


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