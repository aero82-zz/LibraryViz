$(document).ready(function() {
  
  $('.box img').mouseenter(function() {
    $(this).attr('src', $(this).attr('src').replace('normal','curl'))
    console.log($(this).attr('src'))
  }).mouseleave(function() {
    $(this).attr('src', $(this).attr('src').replace('curl','normal'))
  })
  
  $('.box').each(function() {
    if (Math.random() > 2) {
      $(this).addClass('col3')
      var link = $(this).children('img').attr('src')
    }
  })
/* 
  function fetchBooks(key) {
  // Update page as books are loading
    console.log('starting ajax key=' + key)
    $.ajax({
      type: "POST", url: "/fetch.action",
      data: {'key': key},
      success: function() {
        console.log('something')        
      },
      error: function() {
        console.log(data)
      }
    });
  }
   */
  
  
})