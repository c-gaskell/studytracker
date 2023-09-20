function registerCollapsibles() {
    var buttons = document.getElementsByClassName("collapse-button");
    console.log("Got " + buttons.length + " buttons");

    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener("click", function() {
            var content = document.getElementById(this.getAttribute("for"));
            if (!content.classList.contains("collapsible-hidden")) {
                content.classList.add("collapsible-hidden");
                this.classList.add("collapse-button-hidden");
                console.log("Hiding...");
            } else {
                content.classList.remove("collapsible-hidden");
                this.classList.remove("collapse-button-hidden");
                console.log("Showing...");
            }
        });
    }
}
