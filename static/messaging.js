/* #Benjamin Rarrick
#btr21 3929011
#Project 3
#7/16/18
Javascript document to poll and send new messages */

document.addEventListener("DOMContentLoaded", function(event) {

    var roomID = parseInt(window.location.pathname.replace('/room/',''));
    var messageSend = document.getElementById('messageSend');
    messageSend.addEventListener('click', sendMessage);

    //function to send a message
    function sendMessage(){
        var messageText = document.getElementById('newMessage');

        if(messageText.value.length > 0){
            var jsonName = JSON.stringify({message: messageText.value});

            var xhr = new XMLHttpRequest();
            xhr.open("POST", '/send/'+roomID, true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onload = function() {
                if(xhr.status !== 200){
                    alert('Unable to send message. Status: ' + xhr.status);
                }
                else if (xhr.textContent === 'Failed') {
                    alert('Request failed');
                    //room may have been deleted
                }
            };
            xhr.send(jsonName);
            messageText.value = '';
        }

    }
    
    var leaveRoom = document.getElementById('leaveRoom');
    leaveRoom.addEventListener('click', exitRoom);
       
    //function to exit a chatroom
    function exitRoom(){
        var xhr = new XMLHttpRequest();
        xhr.open("POST", '/exitRoom/'+roomID, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function() {
            if(xhr.status !== 200){
                console.log(xhr.textContent);
                alert('Request failed.  Returned status of ' + xhr.status);
            }
            else if (xhr.textContent !== 'Failure') {
                alert('Leaving Room');
                window.location.href = window.location.protocol+'//'+window.location.host+'/main'
            }
        };

        xhr.send(null);

    }
    
    //get all messages for first load
    var latestMessage =-1;
    getLatestMessage(latestMessage);
    
    function getLatestMessage(latestMessage){
        pollMessages(latestMessage, getLatestMessage)
    }
    
    function pollMessages(latestMessage, callback){
        //console.log(latestMessage);
        var jsonName = JSON.stringify({latestMessage: latestMessage});
        var xhr = new XMLHttpRequest();

        xhr.open("POST", '/getMessages/'+roomID, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function() {

            //console.log(xhr.responseText);
            var jsonResponse = JSON.parse(xhr.responseText);

            if(xhr.status !== 200){
                alert('Request failed.  Returned status of ' + xhr.status);
            }
            else if (jsonResponse.hasOwnProperty('error')) {
                //The chatroom has been deleted, alert the user and redirect back to main
                alert('Room Was Deleted');
                window.location.href = window.location.protocol+'//'+ window.location.host +'/main'
            }
            else if(jsonResponse.hasOwnProperty('redirect')) {
                window.location.href = window.location.protocol+'//'+ window.location.host + jsonResponse['redirect'];
            }
            else {
                updateChatRoomList(jsonResponse, callback);
            }
        };
        xhr.send(jsonName);
    }
    
    //update the DOM list wit the messages
    function updateChatRoomList(jsonResponse, callback){
        var newMessages = jsonResponse['newMessages'];
        var latestMessage = jsonResponse['latestMessage'];

        var messageList = document.getElementById('messageList');

        for(var z = 0; z < newMessages.length; z++){
            var message = newMessages[z];

            var newLI = document.createElement('li');
            var msgString = message.senderName + " - "+message.message;
            newLI.textContent = msgString;
            messageList.appendChild(newLI);
        }

        setTimeout(function(){
            callback(latestMessage);
        }, 1000);
    }
});