$(function()
{
    $('input[type=checkbox]').each(function()
    {
        var state = JSON.parse( localStorage.getItem('checkbox_'  + this.id) );

        if (state) this.checked = state.checked;
    });
    $('select[id=country]').each(function() {
        var state = JSON.parse( localStorage.getItem('select_' + this.id));
        if (state) this.value = state.value;
    });
});

$(window).bind('unload', function()
{
    $('input[type=checkbox]').each(function()
    {
        localStorage.setItem(
            'checkbox_' + this.id, JSON.stringify({checked: this.checked})
        );
    });

    $('select[id=country]').each(function() {
        localStorage.setItem(
            'select_' + this.id, JSON.stringify({value: this.value})
        );
    });
});