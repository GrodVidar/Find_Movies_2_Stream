$(document).ready(function() {
    $('#country').select2({
    width: '100%'
    });
    if(storageAvailable('localStorage')){
        $(function()
        {
            $('input[type=checkbox]').each(function()
            {
                var state = JSON.parse( localStorage.getItem('checkbox_'  + this.id) );

                if (state) this.checked = state.checked;
            });
            $('select[id=country]').each(function() {
                var state = JSON.parse( localStorage.getItem('select_' + this.id));
                if (state) $(this).val(state.value).trigger('change');
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
    } else {
        if(document.getElementById('providers')) {
            var providers = document.getElementById('providers').value;
            providers = providers.split(',');
            for (provider of providers) {
                document.getElementById(provider).checked = true;
            }
        }
        if (document.getElementById('selectedCountry')) {
            var country = document.getElementById('selectedCountry').value;
            $('#country').val(country).trigger('change');
        }

    }
})

function format(item, state) {
  if (!item.id) {
    return item.text;
  }
  var countryUrl = "https://hatscripts.github.io/circle-flags/flags/";
  var stateUrl = "https://oxguy3.github.io/flags/svg/us/";
  var url = state ? stateUrl : countryUrl;
  var img = $("<img>", {
    class: "img-flag",
    width: 26,
    src: url + item.element.value.toLowerCase() + ".svg"
  });
  var span = $("<span>", {
    text: " " + item.text
  });
  span.prepend(img);
  return span;
}

function storageAvailable(type) {
    var storage;
    try {
        storage = window[type];
        var x = '__storage_test__';
        storage.setItem(x, x);
        storage.removeItem(x);
        return true;
    }
    catch(e) {
        return e instanceof DOMException && (
            // everything except Firefox
            e.code === 22 ||
            // Firefox
            e.code === 1014 ||
            // test name field too, because code might not be present
            // everything except Firefox
            e.name === 'QuotaExceededError' ||
            // Firefox
            e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
            // acknowledge QuotaExceededError only if there's something already stored
            (storage && storage.length !== 0);
    }
}