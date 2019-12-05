$(function () {

    $('.close').click(function () {
        $('#info').fadeOut(500)
    });
})

// Handle full screen mode toggle
// toggle full screen
function toggleFullScreen() {
    if (!document.fullscreenElement &&    // alternative standard method
        !document.mozFullScreenElement && !document.webkitFullscreenElement) {  // current working methods
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        } else if (document.documentElement.mozRequestFullScreen) {
            document.documentElement.mozRequestFullScreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
        }
    } else {
        if (document.cancelFullScreen) {
            document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
    }
}

$('#fullscreen').click(function () {
    toggleFullScreen();
});

$(window).on('load', function () {
    $('#myModal').modal('toggle');
});

setTimeout(function () {
    $('#myModal').modal('hide');
}, 5000);

$('#events-modal').on('hidden.bs.modal', function () {
    location.reload()
});

function abrir_modal(url) {
    $('#delete').load(url, function () {
        $(this).modal('show');
    });
    return false;
}

function cerrar_modal() {
    $('#popup').modal('hide');
    return false;
}

$(document).ready(function () {
    $('#tabla').dataTable({
        "language": {
            url: "/static/localizacion/es_ES.json"
        }
    });

    $(window).scroll(function () {
        if ($(this).scrollTop() > 200) {
            $('#topcontrol').css({'opacity' : 1});
        } else {
            $('#topcontrol').css({'opacity' : 0});
        }
    });

//Click event to scroll to top
    $('#topcontrol').click(function () {
        $('html, body').animate({scrollTop: 0}, 600);
    });
});
