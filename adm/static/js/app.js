$(function () {

    $('.close').click(function () {
        $('#info').fadeOut(500)
    });
});

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

function open_re_useful_modal(url, id=null) {
    if(id) {
        $(`#dropdown_${id}`).load(url, function () {});
        return false;
    }
    $("#re-useful").load(url, function () {
        $(this).modal('show');
    });
    return false;
}

function close_re_useful_modal() {
    $("#re-useful").modal('hide');
    $("#re-useful div").remove();
    return false;
}

function reload_table(url) {
    $(".table-responsive").load(url);
    return false;
}

$(document).ready(function () {
    // Collapse/Show sidebar menu
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $(this).toggleClass('active');
    });

    // Any anonymous datatable
    var count = $("#tabla").find("tr:first td").length - 1;
    $('#tabla').dataTable({
        "language": {
            url: "/static/localizacion/es_ES.json"
        },
        aaSorting: [],
        columnDefs: [
            {
                orderable: false,
                searchable: false,
                targets: count
            }
        ]
    });

    // Report datatable
    $("#tabla_report").dataTable({
        language: {
            url: '/static/localizacion/es_ES.json'
        },
        ordering: false,
        scrollCollapse: true,
        scrollY: 350,
        paging: false,
        dom: 'Bfrtip',
        buttons: ['excelHtml5'],
        drawCallback: function () {
            $('.dt-buttons')[0].style.visibility = 'hidden';
            $('.dataTables_info')[0].style.visibility = 'hidden';
        }
    });

    // Excel export button for Report datatable
    $('#excel_btn').on('click', function () {
        $('.buttons-excel').click();
    });

    // Hide and show up button when scroll down more than 200 px from top
    $(window).scroll(function () {
        if ($(this).scrollTop() > 200) {
            $('#topcontrol').css({'opacity': 1});
        } else {
            $('#topcontrol').css({'opacity': 0});
        }
    });

    // Click event to scroll to top
    $('#topcontrol').click(function () {
        $('html, body').animate({scrollTop: 0}, 600);
    });
});
