(function () {
  var body = document.body;
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.querySelectorAll(".has-mega > button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.parentElement;
      var open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document.querySelectorAll(".has-mega.open").forEach(function (li) { li.classList.remove("open"); });
      body.classList.remove("nav-open");
    }
  });

  // Table of contents: highlight current section
  var tocLinks = document.querySelectorAll(".toc a[href^='#']");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("active"); });
          var a = map[en.target.id];
          if (a) a.classList.add("active");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  // Insight topic filter
  var filters = document.querySelectorAll("[data-filter]");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var t = btn.getAttribute("data-filter");
      filters.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      document.querySelectorAll("[data-topic]").forEach(function (card) {
        card.classList.toggle("hidden", t !== "all" && card.getAttribute("data-topic") !== t);
      });
    });
  });

  // Contact form: compose an email to the firm
  var form = document.getElementById("contact-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = new FormData(form);
      var subject = "Inquiry: " + (f.get("interest") || "General") + " | " + (f.get("organization") || f.get("name"));
      var lines = [
        "Name: " + f.get("name"),
        "Email: " + f.get("email"),
        "Organization: " + f.get("organization"),
        "Role: " + f.get("role"),
        "Area of interest: " + f.get("interest"),
        "",
        f.get("message")
      ];
      window.location.href = "mailto:" + form.getAttribute("data-to") +
        "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
  }
})();
