function bad_password() {
    document.getElementById("status").innerHTML = "Bad Password";
    document.getElementById("details").innerHTML = "The entered password is not secure and is too short.";
    document.getElementById("suggestion").innerHTML = "Your password should have at least 8 letters, 1 number, and 1 symbol.";

    if (document.getElementById("strength").classList.contains('alert-success')) {
        document.getElementById("strength").classList.remove('alert-success');
        document.getElementById("strength").classList.add('alert-danger');
    }
    else if (document.getElementById("strength").classList.contains('alert-warning')) {
        document.getElementById("strength").classList.remove('alert-warning');
        document.getElementById("strength").classList.add('alert-danger');
    }
}

function medium_password() {
    document.getElementById("status").innerHTML = "Medium Password";
    document.getElementById("details").innerHTML = "The entered password isn't very secure.";
    document.getElementById("suggestion").innerHTML = "Your password could be a little longer, and try to have at least 8 letters, 1 number, 1 symbol";

    if (document.getElementById("strength").classList.contains('alert-success')) {
        document.getElementById("strength").classList.remove('alert-success');
        document.getElementById("strength").classList.add('alert-warning');
    }
    else if (document.getElementById("strength").classList.contains('alert-danger')) {
        document.getElementById("strength").classList.remove('alert-danger');
        document.getElementById("strength").classList.add('alert-warning');
    }
}

function good_password() {
    document.getElementById("status").innerHTML = "Good Password";
    document.getElementById("details").innerHTML = "The entered password seems secure, good job!";
    document.getElementById("suggestion").innerHTML = "Your password seems secure enough, but make sure to enable some form of 2FA and don't forget your password!";

    if (document.getElementById("strength").classList.contains('alert-warning')) {
        document.getElementById("strength").classList.remove('alert-warning');
        document.getElementById("strength").classList.add('alert-success');
    }
    else if (document.getElementById("strength").classList.contains('alert-danger')) {
        document.getElementById("strength").classList.remove('alert-danger');
        document.getElementById("strength").classList.add('alert-success');
    }
}

function check() {

    var password = document.getElementById("super_duper_secret_password").value;
    var chars = password.split('');

    if (password == "") {
        $('#suggestion').hide();
        $('#strength').hide();
        $('#details').hide();
        $('#status').hide();
    }
    else {
        $('#suggestion').show();
        $('#strength').show();
        $('#details').show();
        $('#status').show();
    }

    if (password.length > 7) {
        if (password.length > 11) {
            good_password();
        }
        else {
            medium_password();
        }
    }
    else {
        bad_password();
    }
}

function base() {
    $('#suggestion').hide();
    $('#strength').hide();
    $('#details').hide();
    $('#status').hide();
}

base();

function change_colors() {
    let ids = ['prev_percent_close', 'week_percent_close', 'month_percent_close', 'all_percent_close'];
    let counter = ['prev_prices', 'week_prices', 'month_prices', 'all_prices'];
    for (var i = 0; i < ids.length; i++) {
        console.log(i)
        console.log(ids[i])
        var prev = document.getElementById(ids[i]).innerHTML;
        if (prev.includes('-')) {
            document.getElementById(counter[i]).classList.remove('bg-success');
            document.getElementById(counter[i]).classList.add('bg-danger');
        }
    }
}

window.onload = function() {
    change_colors();
}
