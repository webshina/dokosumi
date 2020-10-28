// rangeバー
var elems = document.getElementsByClassName('valueRange');

for(let i = 0; i < elems.length; i++){
    elemRange = elems[i].getElementsByClassName('range')[0]
    elemRange.addEventListener('input', function(event) {
        
        // テキストボックスからフォーカスを外す
        var active_element = document.activeElement;
        if(active_element){
            active_element.blur();
        }

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

window.onload = function() {
    // URLとパラメータを分ける
    var href = location.href;
    var param = location.search;
    var url = href.replace(param, '');

    // パラメータをエンコード
    param = encodeURIComponent(param);

    // 各SNSのシェアURLと、シェアしたいURL、パラメータ、ハッシュタグを結合
    var twLink_t = document.getElementById('twitter-link-btn').href
    console.log(twLink_t)
    twLink = twLink_t + url + param + '&hashtags=DOKOSUMIYOSHI,どこ住吉'

    // シェアボタンのリンクを置き換える
    // Twitter
    $('#twitter-link-btn').attr('href', twLink);
};