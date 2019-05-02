/* #Benjamin Rarrick
#btr21 3929011
#Project 3
#7/16/18
Javascript document to poll update main.html with all chatrooms available */


document.addEventListener("DOMContentLoaded", function(event) {
    
    var roomName = document.getElementById('roomName');
    var roomCreate = document.getElementById('createRoom');
    
    roomCreate.addEventListener('click', createRoom);
    
    //function to create a new chatroom
    function createRoom(){
        
        var name = roomName.value;
        if(name.length > 0){
            var name_object = JSON.stringify({name: name});
            var xhr = new XMLHttpRequest();
            xhr.open("POST", '/createRoom', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onload = function() {
                if (xhr.status === 200 && xhr.responseText === 'Failure') {
                    alert('Unable to create new room.');
                }
                else if (xhr.status !== 200) {
                    alert('Unable to create new room. Status: ' + xhr.status);
                }
            };
            
            xhr.send(name_object);
            roomName.value = "";
        }
    }
    
    //function to delete a chatroom
    function deleteRoom(eve){
        var xhr = new XMLHttpRequest();
        xhr.open("POST", eve.srcElement.id, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200 && xhr.responseText !== 'Success') {
                alert('Unable to delete the room.');
            }
            else if (xhr.status !== 200) {
                alert('Unable to delete the room. Status: ' + xhr.status);
            }
            else {
                window.location.href = window.location.protocol+'//'
                    + window.location.host +'/main'
            }
        };

        xhr.send(null);
    }
    //initial call to poll the rooms
    pollRooms();
     
    //poll the model for any new rooms that may have been created
    function pollRooms() {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
                var raw_json = JSON.parse(xmlHttp.responseText);
                updateChatRoomList(raw_json.myRooms, raw_json.otherRooms, pollRooms);
            }
        };
        xmlHttp.open("GET", '/pollRooms', true);
        xmlHttp.send(null);
    }
    
    //update the DOM to show the updated list of rooms
    function updateChatRoomList(myRooms, otherRooms, callback){
        if (myRooms.length !== 0){
            var noMyRooms = document.getElementById('noMyRooms');
            noMyRooms.textContent = '';
                        
            var myRoomsList = document.getElementById('myRooms');
            myRoomsList.innerHTML = '';
            for(var i = 0; i < myRooms.length; i++){
                var myRoomInd = document.createElement('li');
                var myRoomJoin = document.createElement('a');
                var myRoomDel = document.createElement('button');
                myRoomDel.id = '/deleteRoom/'+myRooms[i].id;
                myRoomDel.addEventListener('click', deleteRoom,false);
                myRoomInd.textContent = myRooms[i].name+ " ";
                myRoomJoin.textContent = "Join Chat";
                myRoomJoin.href = '/room/'+myRooms[i].id;
                myRoomDel.textContent = "Delete Room";
                myRoomDel.id = '/deleteRoom/'+myRooms[i].id;
                myRoomsList.appendChild(myRoomInd);
                myRoomInd.appendChild(myRoomJoin);
                myRoomInd.appendChild(myRoomDel);
            }
        }
        else{
            var myRoomsList = document.getElementById('myRooms');
            myRoomsList.innerHTML = '';
            var noMyRooms = document.getElementById('noMyRooms');
            noMyRooms.textContent = 'You currently have no rooms available';
        }

        if (otherRooms.length !== 0){
            var noOtherRooms = document.getElementById('noOtherRooms');
            noOtherRooms.textContent = '';
                        
            var otherRoomsList = document.getElementById('otherRooms');
            otherRoomsList.innerHTML = '';
            for(var i = 0; i < otherRooms.length; i++){
                var otherRoomInd = document.createElement('li');
                var otherRoomJoin = document.createElement('a');
                otherRoomInd.textContent = otherRooms[i].name+ " ";
                otherRoomJoin.textContent = "Join Chat";
                otherRoomJoin.href = '/room/'+otherRooms[i].id;
                otherRoomsList.appendChild(otherRoomInd);
                otherRoomInd.appendChild(otherRoomJoin);
            }
        }
        else{
            var otherRoomsList = document.getElementById('otherRooms');
            otherRoomsList.innerHTML = '';
            var noOtherRooms = document.getElementById('noOtherRooms');
            noOtherRooms.textContent = 'There are currently no other chat rooms available';
        }
      
        setTimeout(callback, 1000);
    }
});