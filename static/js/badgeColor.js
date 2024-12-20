document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM fully loaded and parsed");
    const colors = ["#054949", "#490505", "#c0a43f", "#270549", "#AB602F", "#1E4916", "#024a4f", "#003e1e", 
        "#35085f", "#57380c", "#4c0505", "#355417", "#616814", "#005500", "#390039", "#683566", "#520736"];
    let colorIndex = 0;

    function setBadgeColor(badge) {
        badge.style.backgroundColor = colors[colorIndex % colors.length];
        colorIndex++;
    }

    const badges = document.querySelectorAll('.badge');
    badges.forEach(setBadgeColor);

    const observer = new MutationObserver(function(mutationsList) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.classList && node.classList.contains('badge')) {
                        setBadgeColor(node);
                    }
                });
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});