document.getElementById("play").addEventListener("click", function () {
    const toSay = document.getElementById("summary").textContent.trim();
    const utterance = new SpeechSynthesisUtterance(toSay);
    if (speechSynthesis.speaking === true) {
        speechSynthesis.cancel();
        document.getElementById("play").style.color = "black";
    } else {
        speechSynthesis.speak(utterance);
        document.getElementById("play").style.color = "gray";
        speechSynthesis.onend = () => {
            document.getElementById("play").style.color = "black";
        };
    }
});
window.onbeforeunload = function () {
    speechSynthesis.cancel();
};

document.getElementById("copy").addEventListener("click", function () {
    var summary = document.getElementById("summary").innerHTML;
    var formatted = summary.replace(/<br\s*\/?>/gi, "\n");
    navigator.clipboard.writeText(formatted).then(function () {
        alert("Summary has been copied successfully into your clipboard");
    });
});