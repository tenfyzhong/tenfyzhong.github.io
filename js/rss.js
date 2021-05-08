$(function(){
  var clipboard = new Clipboard('#to_copy');

  if ('ontouchstart' in document) {
    $('#to_copy').on('touchstart', function(e){
      var $copysuc = $("<div class='copy-tips'><div class='copy-tips-wrap'>复制成功</div></div>");
      $("body").find(".copy-tips").remove().end().append($copysuc);
      $(".copy-tips").fadeOut(3000);
      $(this).removeClass('copy_ho').removeClass('copied');
    });
  } else {
    $('#to_copy').hover(function(){
      $(this).addClass('copy_ho');
    }, function(){
      $(this).removeClass('copy_ho').removeClass('copied');
    });

    clipboard.on('success', function(){
      $('#to_copy').addClass('copied');
    })
  }
});
