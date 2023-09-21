function registerCollapsibles() {
    var buttons = document.getElementsByClassName("collapse-button");
    console.log("Got " + buttons.length + " buttons");

    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener("click", function() {
            var forArr = this.getAttribute("for").split(" ");
            var content = forArr.map(document.getElementById, document);
            console.log(content);

            if (!content[0].classList.contains("collapsible-hidden")) {
                for (var j = 0; j < content.length; j++) {
                    content[j].classList.add("collapsible-hidden");
                }
                this.classList.add("collapse-button-hidden");
            } else {
                for (var j = 0; j < content.length; j++) {
                    content[j].classList.remove("collapsible-hidden");
                }
                this.classList.remove("collapse-button-hidden");
            }
        });
    }
}
