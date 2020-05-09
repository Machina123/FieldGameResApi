function ready() {
    $("#form-register").submit(function(e) {
        e.preventDefault()
        $.ajax("/register", {
            method: "POST",
            data: {
                "username": $("#username").val(),
                "password": $("#password").val()
            },
            dataType: "json",
            success: function(data, status, jqXHR) {
                alert(data.message)
            }
        })
    })

    $("#form-login").submit(function(e) {
        e.preventDefault()
        $.ajax("/login", {
            method: "POST",
            dataType: "json",
            data: {
                "username": $("#username").val(),
                "password": $("#password").val()
            },
            success: function(data, status, jqXHR) {
                alert(data.message)
            }
        })
    })
}

function logout() {
    $.ajax("/logout/access", {
        method: "POST",
        dataType: "json",
        success: function (data, status, jqXHR) {
            $.ajax("/logout/refresh", {
                method: "POST",
                dataType: "json",
                success: function(dataR, statusR, jqXHRr) {
                    window.location.href = "/"
                }
            })
        }
    })
}

window.addEventListener("DOMContentLoaded", ready, false)