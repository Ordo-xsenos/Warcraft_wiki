document.addEventListener("DOMContentLoaded", function() {
    // Поиск статей
    const searchInput = document.getElementById("search");

    searchInput.addEventListener("input", function() {
        const query = searchInput.value.toLowerCase();
        const links = document.querySelectorAll("nav a");

        links.forEach(link => {
            const text = link.textContent.toLowerCase();
            if (text.includes(query)) {
                link.style.display = "inline";
            } else {
                link.style.display = "none";
            }
        });
    });

    // Динамическая подгрузка статей
    const main = document.querySelector("main");
    document.querySelectorAll("nav a").forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            fetch(this.href)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    main.innerHTML = doc.querySelector("main").innerHTML;
                    history.pushState(null, "", this.href);
                });
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    openFullscreen();
});
