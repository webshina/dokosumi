// 街の名前を取得
var townName = document.getElementById('station_name').innerText

// パラメータをエンコード
townName = encodeURIComponent(townName);

// 各SNSのシェアURLと、シェアしたいURL、パラメータ、ハッシュタグを結合
commerceLink = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3560929&pid=886843625&vc_url=https://cbchintai.com/property/search/?query%5D=" + townName ;

// シェアボタンのリンクを置き換える
var commerceBtn = document.getElementById('commerce-btn')
commerceBtn.href = commerceLink;
