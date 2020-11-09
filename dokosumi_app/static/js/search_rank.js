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

// その他(オプション指定の価値観) 
var $target = document.querySelector('.hidden-target')
var $button = document.querySelector('.hidden-button')
$button.addEventListener('click', function() {
  $target.classList.toggle('is-shown')
//   $button.classList.toggle('is-hidden')
})