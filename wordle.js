
function letter_button(initial, score, row, col)
{
    let $letter = $("<button id='let-" + row + "-" + col + "'>")
        .text(initial).addClass("letter pop-in-element incorrect");
    $letter.click(function()
    {
        let options = ["incorrect", "correct", "misplaced"];
        for( let i = 0; i < options.length; i++ )
        {
            let option = options[i];
            if( $letter.hasClass(option) )
            {
                let j = (i+1)%options.length;
                score[col] = j;
                $letter.removeClass(option);
                $letter.addClass(options[j]);
                break;
            }
        }
    });

    return $letter
}

var guesses = [];

function add_guess(word)
{
    let new_guess = {word: word, score: [0,0,0,0,0]}
    let row = guesses.length;
    guesses.push(new_guess);

    letter_buttons = word.substring(0, 5).split('').map((c, index) => letter_button(c, new_guess.score, row, index));
    setTimeout(function() { letter_buttons[0].focus() }, 11);

    return $("<div>").addClass("guess").append(letter_buttons);
}

function make_dialog(title, message, button_text, handler, text_input)
{
    let $dialog = $("<div id='controls'>").addClass("controls");
    let $title = $("<div>").text(title).addClass("dialog-title");
    $dialog.append($title);
    let $dialog_body = $("<div>").html(message).addClass("dialog-body");
    $dialog.append($dialog_body);

    $control_buttons = $("<div>").addClass("control-buttons");
    let $input = text_input ? $('<input maxlength="5">').addClass("dialog-input") : null;

    if( text_input )
    {
        $dialog.append($input);
        let $enter_button = $("<button>").addClass("next").text("enter");

        $input.keydown(function(evt) {
            if (evt.which == 13)
            {
                $input.remove();
                $control_buttons.remove();
                handler($input.val());
            }
        });

        setTimeout(function() { $input.focus() }, 9);
    }

    $dialog.append($control_buttons);
    if( button_text )
    {
        let $button = $("<button>").addClass("next").text(button_text);
        $control_buttons.append($button);
        $button.click(function()
        {
            $button.remove();
            if( text_input )
            {
                let w = $input.val();
                $input.remove();
                $control_buttons.remove();
                handler(w);
            }
            else
            {
                handler();
            }
        });
        if( !text_input )
        {
            setTimeout(function() { $button.focus() }, 9);
        }
    }

    $("#main").append($dialog);
    $dialog.removeClass("pop-out-element");
    $dialog.addClass("pop-in-element");

    return $dialog;
}

document.addEventListener('DOMContentLoaded', () =>
{
    let $guesses = $("<div id='guesses'>").addClass("guesses");
    $("#main").append($guesses);

    function clear_dialog()
    {
        $dialog.removeClass("pop-in-element");
        $dialog.addClass("pop-out-element");
    }

    function handle_response(response)
    {
        setTimeout(function() {
            $(".letter").removeClass("cite");

            $dialog.remove();

            if( response.next_guess )
            {
                $dialog = make_dialog("Excellent", "Score the guess and hit next again", "Next", next_guess_please, false);
                $guesses.append(add_guess(response.next_guess));
            }
            else
            {
                if (response.entry)
                {
                    $dialog = make_dialog(response.title, response.message, "Enter", reveal_word, true);
                }
                else
                {
                    if (response.gameover)
                    {
                        $dialog = make_dialog(response.title, response.message, "", null, false);
                    }
                    else
                    {
                        $dialog = make_dialog(response.title, response.message, "Next", next_guess_please, false);
                    }
                }

                if (response.cites)
                {
                    for( let i = 0; i < response.cites.length; i++ )
                    {
                        let cite = response.cites[i];
                        $("#let-" + cite[0] + "-" + cite[1]).addClass("cite");
                    }
                }
            }

            if( response.gameover )
            {
                $(".letter").off("click");
                $(".letter").prop('disabled', true);
            }
        }, 300);
    }

    function reveal_word(word)
    {
        clear_dialog()
        $.ajax({
            type: "POST",
            url: "/reveal",
            dataType: 'json',
            data: JSON.stringify({guesses:guesses, word:word}),
            success: handle_response,
        });
    }

    function next_guess_please() {
        clear_dialog()
        $.ajax({
            type: "POST",
            url: "/next",
            dataType: 'json',
            data: JSON.stringify({guesses:guesses}),
            success: handle_response,
        });
    }

    let $dialog = make_dialog(
        "Welcome to Reverse Wordle",
        "In ordinary Wordle, the computer picks a word, and you guess.<br/><br/>In this game, you pick a word, and the computer guesses.<br/><br/>So, pick a word, commit to it, write it down, and then hit the Next button to get the first guess :)",
        "Next",
        next_guess_please,
        false
    );
});
