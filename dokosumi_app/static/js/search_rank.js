// rangeバーの値を更新
var elems = document.getElementsByClassName('valueRange');

for(let i = 0; i < elems.length; i++){
    // rangeバーオブジェクトを取得
    let elemRange = elems[i].getElementsByClassName('range')[0]

    // rangeバーの値を更新するファンクションを定義
    function changeRangeValue(){

        // rangeバーの入力値を取得
        let rangeValue = elems[i].getElementsByClassName('range')[0].value;
        // 価値観オブジェクトを取得
        let value = elems[i].getElementsByClassName('value')[0];
        // 目安オブジェクトを取得
        let description = elems[i].getElementsByClassName('descripion')[0];
    
        //ユーザーに表示している数値をrangeバーの入力値で更新
        value.innerHTML = rangeValue;
        //ユーザーに表示している目安をrangeバーの入力値で更新
        if (rangeValue >= 0 && rangeValue < 33) {
            description.innerHTML = "気にしない"
        } else if(rangeValue >= 33 && rangeValue < 66) {
            description.innerHTML = "気にする"
        } else {
            description.innerHTML = "重要"
        }

    }

    // rangeバーにイベントリスナーを追加
    elemRange.addEventListener('input', function(event) {
        
        // テキストボックスからフォーカスを外す
        var active_element = document.activeElement;
        if(active_element){
            active_element.blur();
        }

        // rangeバーの値を更新するファンクション呼び出し
        changeRangeValue()
        
    }, false);

    // rangeバーに読み込み完了時のイベントリスナーを追加
    window.addEventListener('pageshow', function(event) {

        // rangeバーの値を更新するファンクション呼び出し
        changeRangeValue()

    }, false);

};

// その他(オプション指定の価値観) 
var $target = document.querySelector('.hidden-target')
var $button = document.querySelector('.hidden-button')
$button.addEventListener('click', function() {
  $target.classList.toggle('is-shown')
//   $button.classList.toggle('is-hidden')
})