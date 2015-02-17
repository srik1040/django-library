/**
 * Created by potan on 27.12.14.
 */

var animation_time = 3000;

function hide_elements(){
    if (typeof $('.hidden') != 'undefined'){
        $('.hidden').fadeOut(1, function(){});
    }
}

function appear_quote(nr){
    if (typeof $("#q"+nr) != 'undefined'){
        $("#q"+nr).fadeIn(animation_time, function(){});
    }   
}

function disappear_quote(nr){
    if (typeof $("#q"+nr) != 'undefined'){
        $("#q"+nr).fadeOut(animation_time, function(){});
    }
}

function animate_quote(nr, count){
    appear_quote(nr);
    disappear_quote(nr);
    setTimeout(function () {
        var next = (nr + 1) > count ? 0 : (nr+1)
        animate_quote(next, count);
    }, 2 * animation_time);
}

function animate(){
    var count = $('#count-div').attr('count');
    var actual_nr = 0;

    if (typeof count != 'undefined'){
        if (count > 0) {
            animate_quote(0, count);
        }
    }
}

$(document).ready(function(){
    if (typeof $(".flash") != 'undefined'){
        $(".flash").fadeOut(25000, function(){});
    }

    hide_elements();
    animate();
});


