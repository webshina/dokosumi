var angleScale = {
    angle: 0,
    scale: 1
}
var currentAngle = 1;
var currentScale = 0
    
var gestureArea = document.getElementById('gesture-area')
var scaleElement = document.getElementById('scale-element')
var stmp_text_fix_svg = document.getElementById('stmp_text_fix_svg')
var positionLeft = document.getElementById('positionLeft')
var positionTop = document.getElementById('positionTop')
var angleObj = document.getElementById('angle')
var scaleObj = document.getElementById('scale')

function dragMoveListener (event, currentAngle, currentScale) {
    var target = event.target
    // keep the dragged position in the data-x/data-y attributes
    var x = (parseFloat(target.getAttribute('data-x')) || 0 ) + event.dx
    var y = (parseFloat(target.getAttribute('data-y')) || 0 ) + event.dy

    // update the posiion attributes
    target.setAttribute('data-x', x)
    target.setAttribute('data-y', y)

    // translate the element
    gestureArea.style.transformOrigin = "top left"
    target.style.webkitTransform =
    target.style.transform =
    'translate(' + x + 'px, ' + y + 'px)' + "rotate(" + currentAngle + "deg)" + "scale(" + currentScale + "," + currentScale + ")"
    
    // 親要素からの相対位置を取得
    var gt = $('#gesture-area').position().top
    var it = $('#pict_img').height()
    var gl = $('#gesture-area').position().top
    var il = $('#pict_img').height()
    positionTop.value = Math.round(($('#gesture-area').position().top / $('#pict_img').height()) * 10000) / 10000;
    positionLeft.value = Math.round(($('#gesture-area').position().left / $('#pict_img').width()) * 10000) / 10000;
    // 角度を取得
    angleObj.value = currentAngle
    // サイズを取得
    scaleObj.value = currentScale
}

//読み込み時に
window.onload = function() {
    $('#canvas_wrapper').get(0).width = $('#pict_img').width();
    $('#canvas_wrapper').get(0).height = $('#pict_img').height();
}

interact(gestureArea)
    .gesturable({
        // enable inertial throwing
        inertia: true,

        // keep the element within the area of it's parent
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: document.getElementById('pict_img'),
                endOnly: true
            })
        ],
        
        // enable autoScroll
        autoScroll: true,

        onstart: function (event) {
            angleScale.angle -= event.angle
        },
        
        onmove: function (event) {
            // document.body.appendChild(new Text(event.scale))
            currentAngle = event.angle + angleScale.angle
            if(currentScale > 2){
                currentScale = 2
            }else if(currentScale < 0.5){
                currentScale = 0.5
            }else{
                currentScale = event.scale * angleScale.scale
            }

            // uses the dragMoveListener from the draggable demo above
            dragMoveListener(event, currentAngle, currentScale)
        },

        onend: function (event) {
            angleScale.angle = angleScale.angle + event.angle
            angleScale.scale = angleScale.scale * event.scale
        }

    })

    .draggable({
        // enable inertial throwing
        inertia: true,
        // keep the element within the area of it's parent
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: document.getElementById('pict_img'),
                endOnly: true
            })
        ],
        // enable autoScroll
        autoScroll: true,
       
        // call this function on every dragmove event
        onmove: function (event) {
            currentAngle = angleObj.value
            currentScale = scaleObj.value
            dragMoveListener(event, currentAngle, currentScale)
        }
        
      })

// スタンプの色変更
$(document).on('click', '#colorChangeBottun', function(event) {
    // ボタンの色取得
    var eventDOM = event.target;
    var color = eventDOM.style.background
    
    // スタンプの色変更
    var stmp_text_fix = document.getElementById('stmp_text_fix');
    stmp_text_fix.style.fill = color

})

// スタンプ描写
$(document).on('click', '#add_stmp_btn', function() {

    var stmp_txet = document.getElementById('stmp_text').value;
    
    // 一度文字列の長さを取得し、SVGのサイズを指定
    /// 文字を書き込み
    $('#ruler').text(stmp_txet);
    var width = document.getElementById('ruler').offsetWidth;
    var height = 80;
    /// SVGの幅を調整
    document.getElementById('stmp_text_fix_svg').setAttribute("width", width);

    // 文字描写
    $('#stmp_text_fix').text(stmp_txet);

    // 位置をランダムに変更
    x = Math.random() * (80 - 10) + 10;
    y = Math.random() * (20 - 5) + 5;
    gestureArea.style.left = x + '%';  
    gestureArea.style.top = y + '%';  

    // 角度をランダムに取得
    angle = Math.random() * 20 - 10
    // 変形
    gestureArea.style.transformOrigin = "top left"
    gestureArea.style.transform = "rotate(" + angle + "deg)"

    //角度、サイズ、位置の初期値を入力
    /// 角度を入力
    var angleObj = document.getElementById('angle')
    angleObj.value = angle

    /// サイズを取得
    var scaleObj = document.getElementById('scale')
    scaleObj.value = 1

    /// 位置を入力
    var positionLeft = document.getElementById('positionLeft');
    var positionTop = document.getElementById('positionTop');
    positionLeft.value = $('#gesture-area').position().left / $('#pict_img').width();
    positionTop.value = $('#gesture-area').position().top / $('#pict_img').height();

    // gestureAreaの位置情報を初期化
    gestureArea.setAttribute('data-x', 0)
    gestureArea.setAttribute('data-y', 0)

    //スタンプ確定ボタンを表示
    var commit_stmp_btn = document.getElementById('commit_stmp_btn');
    commit_stmp_btn.style.display = 'inline'

})

// スタンプ確定
$(document).on('click', '#commit_stmp_btn', function() {

    // 何も文字がない場合にアラートを出力
    var stmp_text_fix = document.getElementById('stmp_text_fix');
    if (stmp_text_fix.textContent == ''){
        alert('スタンプの文字を入力してください');
        return
    } 

    // 画像のサイズを取得
    var pict_img = document.getElementById("pict_img");
    var imgWidth = pict_img.naturalWidth;
    var imgHeight = pict_img.naturalHeight;

    // 画像のサイズにcanvasの幅を調整
    var commitCanvas = document.getElementById('commitCanvas');
    commitCanvas.width = imgWidth;
    commitCanvas.height = imgHeight;

    // 回転後の座標を取得
    /// canvas上の座標を取得
    var x = imgWidth * positionLeft.value;
    var y = imgHeight * positionTop.value;

    /// 回転にを反映して、canvas上に描写する座標を微調整
    var angle = angleObj.value;
    var gx = gestureArea.clientWidth * scaleObj.value;
    var gy = gestureArea.clientHeight * scaleObj.value;
    if(angle > 0){
        x = x + (Math.sin(angle * (Math.PI / 180)) * gy)
    }else if(angle < 0){
        y = y + (Math.sin(-angle * (Math.PI / 180)) * gx)
    }
    
    var context = commitCanvas.getContext( "2d" );

    // 角度を取得
    context.translate(x, y);
    context.rotate(angle * Math.PI/180);

    // 拡大・縮小
    context.scale(scaleObj.value, scaleObj.value)

    // コメントをSVGとテキスト間で同期
    var stmp_text = document.getElementById('stmp_text')
    stmp_text.value = stmp_text_fix.textContent
        
    // context.drawImage(img, 0, 0);
    context.font = "80px 'MkPOP'";
    var color = $('#stmp_text_fix').css('fill')
    context.fillStyle = color;
    context.globalAlpha = $('#stmp_text_fix').css('opacity');
    context.textBaseline = "top";
    context.fillText(stmp_text.value, 0, 0);

    var stmp_img = document.getElementById('stmp_img')
    stmp_img.value = commitCanvas.toDataURL()
    
    // base64文字列が描写されるまで待機
    while(stmp_img.value==""){}
    $('#send').click()

})