//読み込み時処理
window.onload = function() {

}

// 画像アップロード処理
function upldPict() {

    var inputToUploadPortfolioImage = $('.upload-portfolio-image')

    // 画像入力フォームボタンをクリック
    inputToUploadPortfolioImage.click()
    // 画像入力フォームから画像がアップロードされたらスタート
    inputToUploadPortfolioImage.off('change').on('change', function(e) {
      if (e.target.files && e.target.files[0]) {
        // 読込中の画像を表示
        var cameraImage = document.getElementById('upldPictBtn');
        cameraImage.style.display = 'none'
        var loadingImage = document.getElementById('loadingImage');
        loadingImage.style.display = ''

        var canvas = document.getElementById('uploadImageCanvas');
        var context = canvas.getContext('2d'); 
        
        var file = e.target.files[0]
        var reader = new FileReader();
        // readerでファイルを読み込んだら開始
        reader.onload = function (e) {
            
            // 画像を作成
            var img = document.createElement('img');
            
            // iphone画像の回転修正
            loadImage.parseMetaData(file, (data) => {
                var options = {
                    canvas: true
                };

                if (data.exif) {
                    options.orientation = data.exif.get('Orientation');
                }

                loadImage(file, (canvas) => {
                    var dataUri = canvas.toDataURL();
                    img.src = dataUri; 
                }, options);
            });

            // canvasに画像＋コメントを表示
            img.onload = function() {
                // 画像の本来のサイズを取得
                var imgWidth = img.width;
                var imgHeight = img.height;

                // 画像のリサイズ後のサイズを取得
                /// 全体の横幅より少し小さくする
                var imgWidthStd = 1000 * 0.95
                var imgHeightStd = img.height * imgWidthStd / imgWidth

                // canvasのサイズを画像にあわせて変更
                canvas.width = 1000;
                canvas.height = imgHeightStd + 50
                
                //ポラロイド風の枠を描写
                context.fillStyle = '#fff'
                context.fillRect(0,0,canvas.width,canvas.height);
                
                // 元画像を削除
                $('.pictBfr').remove();   
                //画像を描写
                context.drawImage(img, canvas.width * 0.025, 50, imgWidthStd, imgHeightStd);
                
                //投稿ボタンを表示
                var upldBtn = document.getElementById('upldBtn');
                upldBtn.style.display = 'inline'
                
                //キャンセルボタンを表示
                var cancelBtn = document.getElementById('cancelBtn');
                cancelBtn.style.display = 'inline'
            }
        }
        // readerでファイルを読み込み
        reader.readAsDataURL(file)
      }

    })
}


// アップロード処理
$(document).on('click', '#upldBtn', function() {

    var commentText = document.getElementById('commentText').value
    var canvas = document.getElementById('uploadImageCanvas')

    // 元コメントをPOST用に退避
    var comment = document.getElementById('comment')
    comment.value = commentText
    
    // 元コメントを削除
    $('.commentBfr').remove();
    
    var context = canvas.getContext('2d')

    // canvasの内容を保存
    canvasData = context.getImageData(0, 0, canvas.width, canvas.height)

    // canvasの高さを画像にあわせて変更
    canvas.height = canvas.height + 160;

    context.putImageData(canvasData, 0, 0)

    // コメント用の枠を描写
    context.fillStyle = '#fff'
    context.fillRect(0, canvas.height - 160, canvas.width, 160);

    // ユーザーの名前を取得
    if ( document.getElementById('print_name').checked ) { 
        var username = "@" + document.getElementById('username').value
    } else {
        var username = "STUPLY"
    }

    // 一度文字列の長さを取得し、サイズを指定
    /// 文字を書き込み
    $('#ruler').text(username);
    var width = document.getElementById('ruler').offsetWidth;

    //写真にユーザーの名前をプリント
    context.fillStyle = '#dddddd'
    context.font = "3vw 'Lobster";
    context.textAlign = "right";
    context.textBaseline = "right";
    context.fillText(username, canvas.width - 15, canvas.height - 30);

    //コメントを描写
    context.fillStyle = '#1A1A1A'
    context.font = "6vw 'MkPOP";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(commentText, canvas.width * 0.5, canvas.height - 90);

    //URIを保存
    var pict_img_base64 = document.getElementById('pict_img_base64');
    pict_img_base64.value = canvas.toDataURL();
    
    //送信ボタンを押下
    $('#send').click()
    
})