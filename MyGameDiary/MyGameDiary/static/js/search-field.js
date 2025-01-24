const searchElement = document.querySelector("#search");

searchElement.addEventListener("input", function() {
    const gameElements = document.querySelectorAll(".game");
    let show;

    gameElements.forEach(game => {
        show = false;
        const highlightElements = game.querySelectorAll(".highlight")

        highlightElements.forEach(highlightElement => {
            const index = highlightElement.innerText.toLowerCase().indexOf(searchElement.value.toLowerCase());
            if(searchElement.value.length > 0) {
                if (index >= 0) {
                    show = true;
                    highlightElement.classList.remove('text-white');
                    highlightElement.classList.add('text-warning');
                } else {
                    highlightElement.classList.remove('text-warning');
                    highlightElement.classList.add('text-white');
                }
            } else {
                show = true;
                highlightElement.classList.remove('text-warning');
                highlightElement.classList.add('text-white');
            }
        });

        if (show) {
           game.classList.remove('d-none');
           game.classList.add('d-flex');
        } else {
           game.classList.remove('d-flex');
           game.classList.add('d-none');
        }
    });

});