function render_abuse_report_form(comment_id) {
    jq('form#form-report').bind("submit", function(event){
        event.preventDefault();
    });
    render_button = 'input#input-render-abuse-cancel-' + comment_id;
    jq(render_button).attr('disabled', 'disabled');
    var holder = 'span#span-reply-form-holder-' + comment_id;
    var form = holder + ' > span#span-reply-form';
    jq(form).slideToggle(700);
    var cancel_button = holder + ' input#input-report-abuse-cancel';
    var qq = jq(cancel_button);
    jq(cancel_button).attr('comment_id', comment_id);
}

function remove_abuse_report_form(comment_id) {
    var holder = 'span#span-reply-form-holder-' + comment_id;
    var form = holder + ' > span#span-reply-form';
    jq(form).slideToggle(700);
    render_button = 'input#input-render-abuse-cancel-' + comment_id;
    jq(render_button).attr('disabled', '');
}
