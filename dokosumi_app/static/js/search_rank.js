// rangeバーの値を更新するファンクションを定義
function changeRangeValue(elem){

    // rangeバーの入力値を取得
    let rangeValue = elem.getElementsByClassName('range')[0].value;
    // 価値観オブジェクトを取得
    let value = elem.getElementsByClassName('value')[0];
    // 目安オブジェクトを取得
    let description = elem.getElementsByClassName('descripion')[0];

    //ユーザーに表示している数値をrangeバーの入力値で更新
    value.innerHTML = rangeValue;
    //ユーザーに表示している目安をrangeバーの入力値で更新
    if (rangeValue >= 0 && rangeValue < 20) {
        description.innerHTML = "気にしない"
    } else if(rangeValue >= 21 && rangeValue < 40) {
        description.innerHTML = "あまり気にしない"
    } else if(rangeValue >= 41 && rangeValue < 60) {
        description.innerHTML = "少し気にする"
    } else if(rangeValue >= 61 && rangeValue < 80) {
        description.innerHTML = "気にする"
    } else {
        description.innerHTML = "重要"
    }

}

// rangeバーの値を更新
var elems = document.getElementsByClassName('valueRange');

for(let i = 0; i < elems.length; i++){

    //rangeinput全体を取得
    let elem = elems[i]

    // rangeバーオブジェクトを取得
    let elemRange = elem.getElementsByClassName('range')[0]

    // rangeバーにイベントリスナーを追加
    elemRange.addEventListener('input', function() {
        
        // テキストボックスからフォーカスを外す
        var active_element = document.activeElement;
        if(active_element){
            active_element.blur();
        }

        // rangeバーの値を更新するファンクション呼び出し
        changeRangeValue(elem)
        
    }, false);

    // rangeバーに読み込み完了時のイベントリスナーを追加
    window.addEventListener('pageshow', function() {

        // rangeバーの値を更新するファンクション呼び出し
        changeRangeValue(elem)

    }, false);

};

// その他(オプション指定の価値観) 
var $target = document.querySelector('.hidden-target')
var $button = document.querySelector('.hidden-button')
$button.addEventListener('click', function() {
  $target.classList.toggle('is-shown')
//   $button.classList.toggle('is-hidden')
})


// 読込中アニメーション 
var $searchButton = document.querySelector('.search-btn')
$searchButton.addEventListener('click', function() {
    var $searchButton = document.querySelector('.search-btn')
    $("#bfr-load").css("display", "none");
    $("#on-load").css("display", "block");
})