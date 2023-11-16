$(document).ready(function() {
    setMathJax();
});

function setMathJax() {
    if(window.MathJax === undefined) {
        setTimeout(setMathJax, 500);
        return;
    }
    window.MathJax.Hub.Queue(function () {
        $(".MathJax").css('padding', '1%');
        $(".MathJax .math").css('width', '');
        $(".MathJax .math > span").css('width', '');
        $(":not(.MathJax_Display) > .MathJax .math > span").css('font-size', '');
        $(".MathJax .math > span > span").css('position', '');
        $(".MathJax .math > span > span > span").css('height', '');
    });
}
