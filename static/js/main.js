// ==========================
// MOBILE MENU TOGGLE
// ==========================

const hamburgerBtn = document.getElementById("hamburger-btn");
const menu = document.getElementById("menu");

function openMenu() {
    if (!menu) return;
    const isOpen = menu.classList.toggle("active");
    if (hamburgerBtn) {
        hamburgerBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
        hamburgerBtn.innerHTML = isOpen
            ? '<i class="fa fa-times"></i>'
            : '<i class="fa fa-bars"></i>';
    }
}

// Close menu when a nav link is clicked (mobile UX)
if (menu) {
    menu.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            menu.classList.remove("active");
            if (hamburgerBtn) {
                hamburgerBtn.setAttribute("aria-expanded", "false");
                hamburgerBtn.innerHTML = '<i class="fa fa-bars"></i>';
            }
        });
    });
}

// Close menu when clicking outside of it
document.addEventListener("click", (e) => {
    if (
        menu &&
        menu.classList.contains("active") &&
        !menu.contains(e.target) &&
        hamburgerBtn &&
        !hamburgerBtn.contains(e.target)
    ) {
        menu.classList.remove("active");
        hamburgerBtn.setAttribute("aria-expanded", "false");
        hamburgerBtn.innerHTML = '<i class="fa fa-bars"></i>';
    }
});




// ==========================
// NAVBAR SCROLL EFFECT
// ==========================

const navbar = document.querySelector(".navbar");

if (navbar) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 80) {
            navbar.style.background = "rgba(11,61,46,.97)";
            navbar.style.boxShadow = "0 5px 25px rgba(0,0,0,.2)";
            navbar.style.height = "60px";
        } else {
            navbar.style.background = "rgba(255,255,255,.12)";
            navbar.style.boxShadow = "none";
            navbar.style.height = "65px";
        }
    }, { passive: true });
}




// ==========================
// COUNTER ANIMATION
// (IntersectionObserver – fires only when stat cards enter viewport)
// ==========================

const statCards = document.querySelectorAll(".stat-card h2");

if (statCards.length > 0) {

    const runCounter = (counter) => {
        const target = counter.getAttribute("data-target");
        if (!target) return;

        const suffix = counter.getAttribute("data-suffix") || "";
        const num    = parseInt(target, 10);
        let count    = 0;

        const step  = Math.ceil(num / 60);
        const timer = setInterval(() => {
            count += step;
            counter.textContent = count + suffix;
            if (count >= num) {
                counter.textContent = target + suffix;
                clearInterval(timer);
            }
        }, 35);
    };

    // Store original values and set data attributes
    statCards.forEach(counter => {
        const text   = counter.textContent.trim();
        const hasPlus = text.includes("+");
        const hasK    = text.toUpperCase().includes("K");

        if (hasPlus && !hasK) {
            // e.g. "10+" or "500+"
            counter.setAttribute("data-target", parseInt(text));
            counter.setAttribute("data-suffix", "+");
            counter.textContent = "0+";
        } else if (hasK) {
            // e.g. "50K+" – keep as text, no animation needed
            return;
        }
        // Non-numeric stat cards (e.g. "ISO") are skipped
    });

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                runCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statCards.forEach(counter => {
        if (counter.hasAttribute("data-target")) {
            counterObserver.observe(counter);
        }
    });
}




// ==========================
// SCROLL REVEAL ANIMATION
// (IntersectionObserver – much more performant than scroll events)
// ==========================

const revealElements = document.querySelectorAll(
    ".section, .product-card, .stat-card, .process-box, .career-card, .contact-box"
);

if (revealElements.length > 0) {

    // Set initial hidden state via JS (so it doesn't affect users with JS disabled)
    revealElements.forEach(el => {
        el.style.opacity    = "0";
        el.style.transform  = "translateY(30px)";
        el.style.transition = "opacity .6s ease, transform .6s ease";
    });

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity   = "1";
                entry.target.style.transform = "translateY(0)";
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    revealElements.forEach(el => revealObserver.observe(el));
}




// ==========================
// GALLERY FILTER
// (uses CSS class toggle for proper grid compatibility)
// ==========================

function filterGallery(category) {

    const items = document.querySelectorAll(".gallery-item");

    items.forEach(item => {
        const itemCategory = item.dataset.category || "";

        if (category === "all" || itemCategory === category) {
            item.classList.remove("gallery-hidden");
        } else {
            item.classList.add("gallery-hidden");
        }
    });

    // Update active button state
    const buttons = document.querySelectorAll(".gallery-filter button");
    buttons.forEach(btn => {
        btn.classList.remove("filter-active");
        if (
            btn.textContent.trim() === category ||
            (category === "all" && btn.textContent.trim() === "All")
        ) {
            btn.classList.add("filter-active");
        }
    });
}