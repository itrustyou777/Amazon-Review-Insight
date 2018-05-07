 $(function(){
  // here the code for text minimiser and maxmiser by faisal khan
    var minimized_elements = $('p.text-viewer');
    
    minimized_elements.each(function(){    
        $(this).css('height', 'auto');
        var t = $(this).text();        
        if(t.length < 250) return;
        
        $(this).html(
            t.slice(0,250)+'<span>... </span><a href="#" class="more"> Read More>> </a>'+
            '<span style="display:none;">'+ t.slice(250,t.length)+' <a href="#" class="less"> << Less </a></span>'
        );
    }); 
    
    $('a.more', minimized_elements).click(function(event){
        event.preventDefault();
        $(this).hide().prev().hide();
        $(this).next().show();        
    });
    
    $('a.less', minimized_elements).click(function(event){
        event.preventDefault();
        $(this).parent().hide().prev().show().prev().show();    
    });
});
