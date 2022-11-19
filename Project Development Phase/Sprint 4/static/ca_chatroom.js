$(document).ready(function () {

    var socket = io.connect('http://127.0.0.1:5000');


    var private_socket = io();
    private_socket.emit('init','');




    $('#send_private_message').on('click', function () {

     
        var recipient =  $('.inp').val();
        console.log(recipient);
        var message_to_send = $('#private_message').val();

        private_socket.emit('private_message', { 'userid': recipient ,'message': message_to_send});
    });

    // $('#send_private_message').on('click', function () {
    //     var recipient = $('#send_to_username').val();
    //     var message_to_send = $('#private_message').val();

    //     private_socket.emit('private_message', { 'username': recipient, 'message': message_to_send });
    // });

    private_socket.on('new_private_message', function (msg) {
        $("#messages").append('<li>'+msg+'</li>');
    });



});