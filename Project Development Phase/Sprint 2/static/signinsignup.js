var toggle=true;
$(document).ready(function(){

    $("#name_id").focusout(function(){
    checkName();
    checkForSubmit();})

    $("#mail_id").focusout(function(){
        checkEmail();
        checkForSubmit();})

    $("#phone_id").focusout(function(){
        checkPhone();
        checkForSubmit(); })



    $("#pass").focusout(function(){
       checkMsg();
       checkForSubmit(); })

      $("mpgbdy").hover(function(){
        animate();
    })

    $("#contact").click(function(){
    $("body").load("index.html");})


    $("#mgpbtn").click(function(){
    $("body").load("form.html");})

    $("#fasttrek").click(function(){
    $("body").load("mainpage.html");
    })

    $(".hiddentxt").hide();

    $("#welcome").click(function(){

    console.log(toggle);
    if(toggle==true){
    $(".hiddentxt").show();
    toggle=false;
    }
    else{
     $(".hiddentxt").hide();
      toggle=true;
    }
    })
})

 function checkForSubmit(){
                var check=false;
                check= checkEmail() &&   checkMsg() ;

                 if(check==true){

                 $("#button").css("background-color", "rgba(0,255, 118, 0.8)");

                 }else{
                 $("#button").css("background-color", "#6392e6");

                 }
                return check;
 }
function checkName(){

         var pattern =/^[a-zA-Z ]+$/;
         var namee = $("#name_id").val();
             if( namee==''){
                        $("#name_id").css("border","none");
                       return false;
              }

             else if(pattern.test(namee) && namee!=''){
             $("#name_id").css("border","1px solid  rgba(0,255, 118, 0.8)");
             return true;
               }

            else{

             $("#name_id").css("border","1px solid red");
              return false;
             }
    }
function checkEmail(){

         var pattern = /^[\w]+@[\w]+\.[\w]{2,3}$/;
         var mail = $("#mail_id").val();
             if( mail==''){
                        $("#mail_id").css("border","1px solid gray");
                         return false;
              }

             else if(pattern.test(mail) && mail!=''){
             $("#mail_id").css("border","1px solid rgba(0,255, 118, 0.8)");
             return true;
               }

            else{

             $("#mail_id").css("border","1px solid red");
             return false;

             }
    }
// function checkPhone(){

//          var pattern = /^\d{10}$/g;
//          var ph = $("#phone_id").val();
//              if( ph==''){
//                         $("#phone_id").css("border","none");
//                          return false;
//               }

//              else if(pattern.test(ph) && ph!=''){
//              $("#phone_id").css("border","1px solid rgba(0,255, 118, 0.8)");
//              return true;
//                }

//             else{

//              $("#phone_id").css("border","1px solid red");
//              return false;

//              }
//     }
function checkMsg(){

    var pattern = /^[\w]*$/;
    var mail = $("#pass").val();
        if( mail==''){
                   $("#pass").css("border","1px solid gray");
                    return false;
         }

        else if(pattern.test(mail) && mail!=''){
        $("#pass").css("border","1px solid rgba(0,255, 118, 0.8)");
        return true;
          }

       else{

        $("#pass").css("border","1px solid red");
        return false;

        }
        }
