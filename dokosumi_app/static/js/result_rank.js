// URLとパラメータを分ける
var href = location.href;
var param = location.search;
var url = href.replace(param, '');

// パラメータをエンコード
param = encodeURIComponent(param);
// 「?」はエンコードしない
param = param.replace('%3F','?');

// 各SNSのシェアURLと、シェアしたいURL、パラメータ、ハッシュタグを結合
var twLink_t = document.getElementById('twitter-link-btn').href
console.log(twLink_t)
twLink = twLink_t + url + param + '&hashtags=どこ住吉,住みよい街,引っ越し'

// シェアボタンのリンクを置き換える
$('#twitter-link-btn').attr('href', twLink);