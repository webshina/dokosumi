//読み込み時処理
window.onload = function() {
    console.log(request.path)
}

$(document).on('click', '#loginForUpload_btn', function() {
    location.href="{% url 'social:begin' 'twitter' %}?next={{ 'upload_pict' }}"
})
