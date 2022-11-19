$(document).ready(function(){
            
            
    $("body").on("click", "#complete", function () {
        var q_id = $(this).data('rep');
        $.ajax({
            url: "/clarified",
            type: "get",
            data: { q_id: q_id }
        });});
        
    var down = false;
    
    $('#notify').click(function(e){
      
        var color = $(this).text();
        if(down){
            
            $('#box').css('height','0px');
            $('#box').css('opacity','0');
            down = false;
        }else{
            
            $('#box').css('height','auto');
            $('#box').css('opacity','1');
            down = true;
            
        }
        
    });
        
 
        })
  