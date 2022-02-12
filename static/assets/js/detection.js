
$(function(){
    $('#input-file').change(function(){    
      
        var input = this;
        var url = $(this).val();
        var ext = url.substring(url.lastIndexOf('.') + 1).toLowerCase();
        if (input.files && input.files[0]&& (ext == "gif" || ext == "png" || ext == "jpeg" || ext == "jpg"))
        {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#img').attr('src', e.target.result);
            }
            reader.readAsDataURL(input.files[0]);
        }
        else
        {
            console.log("ha");
        }
    });

});

// document.forms['form'].addEventListener('submit', (event) => {
//     event.preventDefault();
//     // TODO do something here to show user that form is being submitted
//     fetch(event.target.action, {
//         method: 'POST',
//         body: new URLSearchParams(new FormData(event.target)) // event.target is the form
//     }).then((resp) => {
//         return resp.json(); // or resp.text() or whatever the server sends
        
        
//     }).then((body) => {
//         // TODO handle body
//     }).catch((error) => {
//         // TODO handle error
//     });
// });

$("#input-submit").click(function (e) {

    //e.preventDefault(); // prevent actual form submit
    var form = $('#form');
    var url = form.attr('action');
    let myForm = document.getElementById('form');
    var formData = new FormData(myForm);
    
    $('#spinner').css('display', 'block');
    $('#img').css('opacity', '0.5');
    
    $.ajax({
         type: "POST",
         url: 'detect-img',
         data: formData, //form.serialize(), // serializes form input
         success: function(data){
             $('#spinner').attr("style", "display: none !important");
             $('#img').css('opacity', '1.0');
             //console.log('data');
             $('#img').attr('src', 'data:image/png;base64, ' + data);
         },
        error: function(e) {
             $('#spinner').attr("style", "display: none !important");
            $('#img').css('opacity', '1.0');
        },
        cache: false,
        contentType: false,
        processData: false
    });
    e.preventDefault(); // prevent actual form submit
});

$('#settings-depth').change(function (e) {
   $('#detection-percentage').html($('#settings-depth')[0].value + '%');
});


$('#settings-depth').on('input', function (e) {
   $('#detection-percentage').html($('#settings-depth')[0].value + '%');
});


