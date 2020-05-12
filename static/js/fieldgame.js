function getGames() {
    $.ajax("/games", {
        method: "GET",
        dataType: "json",
        success: function (data, status, jqXHR) {
            var tableBody = $("#game-details");
            for(var game of data.games) {
                var row = $("<tr>");
                var cellName = $("<td>").text(game.title)
                var cellDescription = $("<td>").text(game.description)
                var cellRiddles = $("<td>").text(game.riddles)
                var cellJoinButton = $("<td>");
                var buttonJoin = document.createElement("button")
                buttonJoin.className = "btn btn-success"
                buttonJoin.innerText = "Join >"
                buttonJoin.onclick = function() {showJoinGameModal(game.id)}
                cellJoinButton.append(buttonJoin)
                row.append(cellName, cellDescription, cellRiddles, cellJoinButton);
                tableBody.append(row);
            }
        }
    })
}

function getStatistics() {
    $.ajax("/stats", {
        method: "GET",
        dataType: "json",
        success: function(data, status, jqXHR) {
            var list = data.entries
            list.sort(statSorter);
            var tableBody = $("#stat-details")
            for(var entry of list) {
                var row = $("<tr>");
                var cellUsername = $("<td>").text(entry.username)
                var cellGameName = $("<td>").text(entry.game)
                var cellPlayTime = $("<td>").text((entry.finished === true ? "Finished in " : "Playing for ") + formatTime(entry.elapsed_seconds))
                row.append(cellUsername, cellGameName, cellPlayTime);
                tableBody.append(row);
            }
        }
    })
}

function statSorter(a, b) {
    return (a.finished > b.finished) ? 1 : ((a.finished === b.finished) ? ((a.elapsed_seconds > b.elapsed_seconds)? 1 : -1) : -1)
}

function formatTime(totalSeconds) {
    var hours   = Math.floor(totalSeconds / 3600)
    var minutes = Math.floor(totalSeconds / 60) % 60
    var seconds = Math.floor(totalSeconds % 60)
    return hours + "h " + minutes + "m " + seconds + "s";
}

function showJoinGameModal(gameId) {
    let uri = encodeURIComponent("https://fieldgameapi.herokuapp.com/mygames/" + gameId + "/start")
    $("#gameQR").attr("src", "http://api.qrserver.com/v1/create-qr-code/?data="+ uri +"&size=400x400")
    $("#gameDetailModal").modal("show");
}