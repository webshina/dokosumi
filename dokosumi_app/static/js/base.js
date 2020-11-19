// メニューバー
$(function(){

	//ハンバーガーボタンをクリックしたときの処理
	$('#hamburgerbtn').click(function(){
		$('#glaylayer:not(:animated)').fadeIn('fast');
		$('#slidemenu:not(:animated)').css({
			'left' : -1*$('#slidemenu').width(),
			'display' : 'block'	
		}).animate({
			'left' : 0
		},'fast');
	});
	
	//背景をクリックしたときの処理
	$('#glaylayer').click(function(){
		$('#glaylayer:not(:animated)').fadeOut('fast');
		$('#slidemenu:not(:animated)').animate({
			'left' : -1*$(this).width()
		},'fast',function(){
			$(this).css({
				'display' : 'none'	
			});
		});
	});
	
});