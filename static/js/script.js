$(function()
{
    $('input[type=checkbox]').each(function()
    {
        var state = JSON.parse( localStorage.getItem('checkbox_'  + this.id) );

        if (state) this.checked = state.checked;
    });
    $('#country')
});

$(window).bind('unload', function()
{
    $('input[type=checkbox]').each(function()
    {
        localStorage.setItem(
            'checkbox_' + this.id, JSON.stringify({checked: this.checked})
        );
    });
});