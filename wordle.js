
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
    setTimeout(function() { letter_buttons[0].focus() }, 10);

    return $("<div>").addClass("guess").append(letter_buttons);
}

document.addEventListener('DOMContentLoaded', () =>
{
    let $guesses = $("<div id='guesses'>").addClass("guesses");
    let $controls = $("<div id='controls'>").addClass("controls");

    let $title = $("<div>").text("Welcome to Reverse Wordle").addClass("dialog-title")
    $controls.append($title)

    let $dialog_body = $("<div>").html("In ordinary Wordle, the computer picks a word, and you guess.<br/><br/>In this game, you pick a word, and the computer guesses.<br/><br/>So, pick a word, commit to it, write it down, and then hit the next button to get the first guess :)").addClass("dialog-body");
    $controls.append($dialog_body)

    $control_buttons = $("<div>").addClass("control-buttons");
    $("#main").append([$guesses, $controls]);
    $controls.append($control_buttons);

    let $next_button = $("<button>").addClass("next").text("next");
    $control_buttons.append($next_button);

    setTimeout(function() { $next_button.focus() }, 10);

    function clear_dialog()
    {
        $controls.removeClass("pop-in-element")
        $controls.addClass("pop-out-element")
    }

    $next_button.click(function() {
        clear_dialog()
        $.ajax({
            type: "POST",
            url: "/next",
            dataType: 'json',
            data: JSON.stringify({guesses:guesses}),
            success: function(response)
            {
                setTimeout(function() {
                    $controls.removeClass("pop-out-element")
                    $controls.addClass("pop-in-element")
                    $(".letter").removeClass("cite");
                    if( response.next )
                    {
                        $title.text("Excellent");
                        $dialog_body.text("Score the guess and hit next again");
                        $guesses.append(add_guess(response.next));
                    }
                    else
                    {
                        if (response.cites)
                        {
                            for( let i = 0; i < response.cites.length; i++ )
                            {
                                let cite = response.cites[i];
                                $("#let-" + cite[0] + "-" + cite[1]).addClass("cite");
                            }
                        }

                        $title.text(response.title);
                        $dialog_body.text(response.message);
                    }

                    if( response.gameover )
                    {
                        $next_button.remove();
                        $(".letter").off("click");
                        $(".letter").prop('disabled', true);
                    }
                }, 300);
            },
        });
    });
    $controls.addClass("pop-in-element")
});
