// Logout if idle
var logoutWhenIdle = function() {
    var time;
    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;

    function logout() {
        $.redirect('/logout_handler');
    };

    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(logout, 1000 * 60 * 30); // 1000 milliseconds * 60 seconds = 1 minute * 30 = 30minutes;
    };
};

// Custom Password character checker
function validateInput(input) {
    var pass = $(input).val();
    var confirm_submit = false;

    var confirm_uppercase = pass.match(/[A-Z]/g);
    if (confirm_uppercase) {
        checkErrors('uppercase', error = false);

    } else {
        checkErrors('uppercase', error = true);

    };

    var confirm_lowercase = pass.match(/[a-z]/g);
    if (confirm_lowercase) {
        checkErrors('lowercase', error = false);

    } else {
        checkErrors('lowercase', error = true);

    };

    var confirm_digit = pass.match(/[0-9]/g);
    if (confirm_digit) {
        checkErrors('digit', error = false);

    } else {
        checkErrors('digit', error = true);

    };

    var confirm_special = pass.match(/([., ,, !, %, &, @, #, $, ^, *, ?, _, ~])/);
    if (confirm_special) {
        checkErrors('special', error = false);

    } else {
        checkErrors('special', error = true);

    };

    var confirm_length = pass.length >= 10;
    if (confirm_length) {
        checkErrors('length', error = false);

    } else {
        checkErrors('length', error = true);

    };

    if (confirm_uppercase && confirm_lowercase && confirm_digit && confirm_special && confirm_length) {
        confirm_submit = true;

    };
    return confirm_submit;
};

function checkErrors(selector, error = true) {
    var green = $('#' + selector + ' .fa-check-circle');
    var red = $('#' + selector + ' .fa-times-circle');

    if (error) {
        red.removeClass('hidden');
        green.addClass('hidden');

    } else {
        red.addClass('hidden');
        green.removeClass('hidden');
    };
};

// Custom options for Full Calendar plugin
function createDatepicker(selector, maxDate = undefined) {
    $(selector).datetimepicker({
        format: 'DD/MM/YYYY',
        date: $(selector).val(),
        maxDate: maxDate,
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-chevron-up",
            down: "fa fa-chevron-down",
            previous: 'fa fa-chevron-left',
            next: 'fa fa-chevron-right',
            today: 'fa fa-screenshot',
            clear: 'fa fa-trash',
            close: 'fa fa-remove'
        },
        widgetPositioning: {
            horizontal: 'right',
            vertical: 'bottom'
        },
    });
};

// Focus on first input on the page and inside a bootstrap modal
function focusOnInput() {
    // Focus on page load
    $('input:not(:disabled):not(.search_sidebar):visible:first').focus();
    // Focus on modal open
    $(document).on('shown.bs.modal', function(e) {
        $('input:visible:enabled:first', e.target).focus();
    });
    // Focus on modal close
    $(document).on('hidden.bs.modal', function(e) {
        $('input:not(:disabled):not(.search_sidebar):visible:first').focus();
    });
};

// Get Object of form data for selector
function getFormData(selector) {
    var inputdict = $(selector).serializeArray();
    var outputdict = new Object;
    $.map(inputdict, function(n, i) {
        outputdict[n['name']] = n['value'];
    });
    return outputdict;
};

// Custom PDF download function
function exportFile(selector, href_with_formserial, focus = true) {
    $(selector).click(function() {
        $.get(href_with_formserial, function(data) {
            if (focus === true) {
                var win = window.open(href_with_formserial, '_blank');
                win.focus();
            } else {
                window.location = href_with_formserial;
            };
            return false;
        });
    });
};

// Custom image-not-found error handler
function ImageNotFoundHandler(selector, person = true) {
    $(selector).on('error', function() {
        if (person) {
            $(this).attr('src', '/images/nobody.png');
        } else {
            $(this).attr('src', '/images/nothing.png');
        }
    });
}

// Custom dynamic window resizer
function WindowResizer(selector) {
    $(window).resize(function() {
        var width = $(window).width();
        var inner_width = width - 20;
        $("body").css('width', width + 'px');
        $("body").css('height', '100%');
        $(selector).css('width', inner_width + 'px');
    })
    $(window).trigger("resize");
}

// Custom options for the jquery.validate.js plugin
function setFormValidation(id) {
    $(id).validate({
        highlight: function(element) {
            $(element).closest('.form-group').removeClass('has-success').addClass('has-danger');
            $(element).closest('.form-check').removeClass('has-success').addClass('has-danger');
        },
        success: function(element) {
            $(element).closest('.form-group').removeClass('has-danger').addClass('has-success');
            $(element).closest('.form-check').removeClass('has-danger').addClass('has-success');
            (element).remove();
        },
        errorPlacement: function(error, element) {
            if (error['0'].innerText.length != 0) {
                $(element).closest('.form-group').append(error);
            }
        },
        invalidHandler: function(form, validator) {
            var errors = validator.numberOfInvalids();
            if (errors) {
                var focus = $('input:focus').length;
                if (focus == 0) {
                    validator.errorList[0].element.focus();
                };
            };
        },
    });
}

function FormIsValid(form_selector) {
    return $(form_selector).valid(); // Boolean
}


function showNotification(color = 'danger', message) {
    if (message == '' || undefined) {
        return
    }
    if (color == 'danger' || 'warning') {
        type_icon = 'exclamation-circle';
    } else if (color == 'info') {
        type_icon = 'info-circle';
    } else if (color == 'success') {
        type_icon = 'check-circle';
    } else {
        type_icon = 'exclamation-circle';
    }
    $.notify({
        icon: "fas fa-" + type_icon,
        message: message

    }, {
        type: color,
        timer: 5000,
        placement: {
            from: 'top',
            align: 'right'
        }
    });
}

function validateFile(element_id, max_size, allowed_types = /(\.jpg|\.png|\.jpeg|\.pdf|\.xlsx)$/, message_types='.jpg, .jpeg, .png, .pdf or .xlsx') {
    var thisFile = document.getElementById(element_id);
    var fileVal = thisFile.value;
    if (fileVal != '') {
        var checkImg = fileVal.toLowerCase();
        if (!checkImg.match(allowed_types)) {
            showNotification(
                "danger",
                "The selected file's filetype is incorrect.<br/>" +
                `Please select a file with ${message_types} file extension.`
            );
            thisFile.value = '';
            return false;
        }
        if (thisFile.files[0].size > (max_size * 1024 * 1024)) {
            showNotification('danger', `The selected file is larger than ${max_size}MB.  Please select a smaller file.`);
            thisFile.value = '';
            return false;
        }
        return true;
    }
}

function validatePassword(password, pattern, selector, checkVar) {
    if (password.match(pattern)) {
        $('#' + selector + ' .fa-check-circle').removeAttr('hidden');
        $('#' + selector + ' .fa-times-circle').attr('hidden', 'hidden');
        window[checkVar] = true;
        console.log(checkVar, true)
    } else {
        $('#' + selector + ' .fa-check-circle').attr('hidden', 'hidden');
        $('#' + selector + ' .fa-times-circle').removeAttr('hidden');
        window[checkVar] = false;
        console.log(checkVar, false)
    }
};
// Ajax File upload with jQuery and XHR2
// Sean Clark http://square-bracket.com
// xhr2 file upload
$.fn.upload = function(remote, data, successFn, progressFn) {
    // if we dont have post data, move it along
    if (typeof data != "object") {
        progressFn = successFn;
        successFn = data;
    }
    var formData = new FormData();
    var numFiles = 0;
    this.each(function() {
        var i, length = this.files.length;
        numFiles += length;
        for (i = 0; i < length; i++) {
            formData.append(this.name, this.files[i]);
        }
    });
    // if we have post data too
    if (typeof data == "object") {
        for (var i in data) {
            formData.append(i, data[i]);
        }
    }
    var def = new $.Deferred();
    if (numFiles > 0) {
        // do the ajax request
        $.ajax({
            url: remote,
            type: "POST",
            xhr: function() {
                myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload && progressFn) {
                    myXhr.upload.addEventListener("progress", function(prog) {
                        var value = ~~((prog.loaded / prog.total) * 100);
                        // if we passed a progress function
                        if (typeof progressFn === "function") {
                            progressFn(prog, value);
                            // if we passed a progress element
                        } else if (progressFn) {
                            $(progressFn).val(value);
                        }
                    }, false);
                }
                return myXhr;
            },
            data: formData,
            dataType: "json",
            cache: false,
            contentType: false,
            processData: false,
            complete: function(res) {
                var returnValue;
                try {
                    returnValue = JSON.parse(res.responseText);
                } catch (e) {
                    returnValue = res.responseText;
                }
                if (typeof successFn === "function") successFn(returnValue);
                def.resolve(returnValue);
            }
        });
    } else {
        def.reject();
    }
    return def.promise();
};
var addLoginClick = function(selector) {
    $(selector).click(function() {
        $("#dialogdiv").load("/get_login_modal?", function() {
            return false;
        });
    });
};


/*!
 * stars.js
 * https://github.com/viniciusmichelutti/jquery-stars
 *
 * Released under the MIT license
 * https://github.com/viniciusmichelutti/jquery-stars/blob/master/LICENSE
 */
(function($) {

    $.fn.stars = function(options) {

        var settings = $.extend({
            stars: 5,
            emptyIcon: 'fa-star-o',
            filledIcon: 'fa-star',
            color: '#E4AD22',
            starClass: '',
            value: 0,
            text: null,
            click: function() {}
        }, options);

        var block = this;

        for (var x = 0; x < settings.stars; x++) {
            var icon = $("<i>").addClass("fa").addClass(settings.emptyIcon).addClass(settings.starClass);

            if (settings.text) {
                icon.attr("data-rating-text", settings.text[x]);
            }

            if (settings.color !== "none") {
                icon.css("color", settings.color)
            }

            this.append(icon);
        }

        if (settings.text) {
            var textDiv = $("<div>").addClass("rating-text");
            this.append(textDiv);
        }

        var stars = this.find("i");

        stars.on("mouseover", function() {
            var index = $(this).index() + 1;
            var starsHovered = stars.slice(0, index);
            events.removeFilledStars(stars, settings);
            events.fillStars(starsHovered, settings);

            if (settings.text) block.find(".rating-text").html($(this).data("rating-text"));
        }).on("mouseout", function() {
            events.removeFilledStars(stars, settings);
            events.fillStars(stars.filter(".selected"), settings);
            if (settings.text) block.find(".rating-text").html("");
        }).on("click", function() {
            var index = $(this).index();
            settings.value = index + 1;
            stars.removeClass("selected").slice(0, settings.value).addClass("selected");
            settings.click.call(stars.get(index), settings.value);
        });

        events = {
            removeFilledStars: function(stars, s) {
                stars.removeClass(s.filledIcon).addClass(s.emptyIcon);
                return stars;
            },

            fillStars: function(stars, s) {
                stars.removeClass(s.emptyIcon).addClass(s.filledIcon);
                return stars;
            }
        };

        if (settings.value > 0) {
            var starsToSelect = stars.slice(0, settings.value);
            events.fillStars(starsToSelect, settings).addClass("selected");
        }

        return this;
    };
}(jQuery));


charts = {
    initCharts: function() {
        var dataPerformance = {
            labels: ['9pm', '2am', '8am', '2pm', '8pm', '11pm', '4am'],
            series: [
                [1, 6, 8, 7, 4, 7, 8, 12, 16, 17, 14, 13]
            ]
        };

        var optionsPerformance = {
            showPoint: false,
            lineSmooth: true,
            axisX: {
                showGrid: false,
                showLabel: true
            },
            axisY: {
                offset: 40,
            },
            low: 0,
            high: 16
        };
        Chartist.Line('#chartPerformance', dataPerformance, optionsPerformance);

        var dataStock = {
            labels: ['\'07', '\'08', '\'09', '\'10', '\'11', '\'12', '\'13', '\'14', '\'15'],
            series: [
                [22.20, 34.90, 42.28, 51.93, 62.21, 80.23, 62.21, 78.83, 82.12, 102.50, 107.23]
            ]
        };
    }
}

// Logout user if they open a new tab.
function logoutOnNewTab() {
    localStorage.open_pages = Date.now();

    var onLocalStorageEvent = function(e) {
        if (e.key == 'open_pages') {
            $.redirect('/logout_handler');
        };
    };
    window.addEventListener('storage', onLocalStorageEvent, false);
};

// Wizard
function createWizard(selector, onNext_func, onLast_func) {
    $(selector).bootstrapWizard({
        'tabClass': 'nav nav-pills',
        'nextSelector': '.btn-next',
        'previousSelector': '.btn-previous',
        'lastSelector': '.btn-finish',

        onNext: onNext_func,

        onLast: onLast_func,

        onInit: function(tab, navigation, index) {
            //check number of tabs and fill the entire row
            var $total = navigation.find('li').length;
            var $wizard = navigation.closest(selector);

            active_li = navigation.find('li.active:first-child a').html();
            $moving_div = $("<div class='moving-tab'></div>");
            $moving_div.append(active_li);
            $(selector + ' .wizard-navigation').append($moving_div);

            refreshAnimation($wizard, index);

            $('.moving-tab').css('transition', 'transform 0s');
        },

        onTabClick: function(tab, navigation, index) {
            return true;
        },

        onTabShow: function(tab, navigation, index) {
            var $total = navigation.find('li').length;
            var $current = index + 1;

            var $wizard = navigation.closest(selector);

            // If it's the last tab then hide the last button and show the finish instead
            if ($current >= $total) {
                $($wizard).find('.btn-next').hide();
                $($wizard).find('.btn-finish').show();
            } else {
                $($wizard).find('.btn-next').show();
                $($wizard).find('.btn-finish').hide();
            }

            button_text = navigation.find('li:nth-child(' + $current + ') a').html();

            setTimeout(function() {
                $('.moving-tab').html(button_text);
            }, 150);

            var checkbox = $('.footer-checkbox');

            if (!index == 0) {
                $(checkbox).css({
                    'opacity': '0',
                    'visibility': 'hidden',
                    'position': 'absolute'
                });
            } else {
                $(checkbox).css({
                    'opacity': '1',
                    'visibility': 'visible'
                });
            }

            refreshAnimation($wizard, index);
        }
    });


    $(window).resize(function() {
        $(selector).each(function() {
            $wizard = $(this);

            index = $wizard.bootstrapWizard('currentIndex');
            refreshAnimation($wizard, index);

            $('.moving-tab').css({
                'transition': 'transform 0s'
            });
        });
    });

    function refreshAnimation($wizard, index) {
        $total = $wizard.find('.nav li').length;
        $li_width = 100 / $total;

        total_steps = $wizard.find('.nav li').length;
        move_distance = $wizard.width() / total_steps;
        index_temp = index;
        vertical_level = 0;

        mobile_device = $(document).width() < 600 && $total > 3;

        if (mobile_device) {
            move_distance = $wizard.width() / 2;
            index_temp = index % 2;
            $li_width = 50;
        }

        $wizard.find('.nav li').css('width', $li_width + '%');

        step_width = move_distance;
        move_distance = move_distance * index_temp;

        $current = index + 1;

        if (mobile_device) {
            vertical_level = parseInt(index / 2);
            vertical_level = vertical_level * 38;
        }

        $wizard.find('.moving-tab').css('width', step_width);
        $('.moving-tab').css({
            'transform': 'translate3d(' + move_distance + 'px, ' + vertical_level + 'px, 0)',
            'transition': 'all 0.5s cubic-bezier(0.29, 1.42, 0.79, 1)'

        });
    }
};

function initForm(form_selector, button_id, success_func) {
    var form = $(form_selector);
    setFormValidation(form);
    $(button_id).click(function() {
        var valid = FormIsValid(form);
        if (valid) {
            var url = $(form).data('url');
            var formserial = getFormData(form);
            $.post(url, formserial, function(data) {
                var result = JSON.parse(data);
                showNotification(result.status, result.message);
                if (result.success === true) {
                    success_func();
                    return false;
                };
            });
        }
    });
}

$(document).on('change', 'input[type="file"]', function(e) {
    var thisId = $(this).attr('id');
    var data = $(this).data();
    var result;
    if (data.type !== undefined){
        console.log('Here we are, this should be docx')
        var message_type = (data.message_type !== undefined) ? data.message : data.type;
        result = validateFile(thisId, 5, data.type, message_type);
    } else {
        var result = validateFile(thisId, 5);
    }

    var firstFile = e.target.files[0];
    var fileName = 'Choose file...'
    if (firstFile !== undefined) {
        fileName = e.target.files[0].name;
    }
    $('label[for="' + thisId + '"]').text(fileName);
    return false;
});
var sweet_loader = '<div class="sweet_loader"><svg viewBox="0 0 140 140" width="140" height="140"><g class="outline"><path d="m 70 28 a 1 1 0 0 0 0 84 a 1 1 0 0 0 0 -84" stroke="rgba(0,0,0,0.1)" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"></path></g><g class="circle"><path d="m 70 28 a 1 1 0 0 0 0 84 a 1 1 0 0 0 0 -84" stroke="#71BBFF" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dashoffset="200" stroke-dasharray="300"></path></g></svg></div>';


$(function() {
    $('[data-toggle="tooltip"]').tooltip()
})

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
}

function eraseCookie(key) {
    var keyValue = getCookie(key);
    setCookie(key, keyValue, '-1');
}

function setCookie(key, value, expiry) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (expiry * 24 * 60 * 60 * 1000));
    document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
}
