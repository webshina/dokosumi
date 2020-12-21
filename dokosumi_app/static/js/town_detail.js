window.onload = function() {
    // アフィリエイトリンク生成
    var elems = document.getElementsByClassName('commerce-btn');

    // // CB賃貸版
    // for(let i = 0; i < elems.length; i++){
    //     // 街の名前を取得
    //     var townName = elems[i].name
    //     // パラメータをエンコード
    //     townName = encodeURIComponent(townName);
    //     // 各SNSのシェアURLと、シェアしたいURL、パラメータ、ハッシュタグを結合
    //     commerceLink = "https://cbchintai.com/property/search/?query%5D=" + townName ;
    //     // シェアボタンのリンクを置き換える
    //     elems[i].href = commerceLink;
    // };

    // SUUMO版
    for(let i = 0; i < elems.length; i++){
        // 都道府県名を取得
        var pref = elems[i].getElementsByClassName('pref')[0].innerHTML;
        
        // SUUMO駅コードを取得
        var suumoEkiCode = elems[i].getElementsByClassName('suumoEkiCode')[0].innerHTML;

        // 各SNSのシェアURLと、シェアしたいURL、パラメータ、ハッシュタグを結合
        commerceLink = "https://suumo.jp/chintai/" + pref + "/ek_" + suumoEkiCode + "/";
        // シェアボタンのリンクを置き換える
        elems[i].href = commerceLink;
    };
};
