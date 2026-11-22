(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var nav = document.getElementById("nav");
    var hero = document.getElementById("hero");
    var heroMedia = document.getElementById("heroMedia");
    var heroContent = document.getElementById("heroContent");
    var toggle = document.getElementById("navToggle");

    /* ----- Accueil : nav opaque après l'image + parallaxe ----- */
    if (nav && hero) {
        var ticking = false;

        var update = function () {
            var y = window.scrollY;
            var h = hero.offsetHeight;

            nav.classList.toggle("is-solid", y > h - 80);

            if (!reduceMotion && y <= h) {
                heroMedia.style.transform = "translate3d(0," + (y * 0.35) + "px,0)";
                heroContent.style.transform = "translate3d(0," + (y * 0.15) + "px,0)";
                heroContent.style.opacity = String(Math.max(0, 1 - (y / h) * 1.4));
            }
            ticking = false;
        };

        var onScroll = function () {
            if (!ticking) {
                ticking = true;
                requestAnimationFrame(update);
            }
        };

        window.addEventListener("scroll", onScroll, { passive: true });
        window.addEventListener("resize", onScroll);
        update();
    }

    /* ----- Menu mobile ----- */
    if (nav && toggle) {
        var setOpen = function (open) {
            nav.classList.toggle("is-open", open);
            toggle.setAttribute("aria-expanded", String(open));
            toggle.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
            document.body.style.overflow = open ? "hidden" : "";
        };

        toggle.addEventListener("click", function () {
            setOpen(!nav.classList.contains("is-open"));
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") setOpen(false);
        });
    }

    /* ----- Bouton Afficher / Masquer sur les mots de passe ----- */
    document.querySelectorAll('.field input[type="password"]').forEach(function (input) {
        var wrap = document.createElement("div");
        wrap.className = "pw-wrap";
        input.parentNode.insertBefore(wrap, input);
        wrap.appendChild(input);

        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "pw-toggle";
        btn.textContent = "Afficher";
        btn.addEventListener("click", function () {
            var hidden = input.type === "password";
            input.type = hidden ? "text" : "password";
            btn.textContent = hidden ? "Masquer" : "Afficher";
            input.focus();
        });
        wrap.appendChild(btn);
    });

    /* ----- Filtres de la page "Mes articles" ----- */
    var filters = document.querySelectorAll("[data-filter]");          // les 3 boutons Tous / Publiés / Brouillons
    var rows = document.querySelectorAll(".post-row");                  // les lignes d'articles
    var filterEmpty = document.getElementById("filterEmpty");           // message "aucun article"

    filters.forEach(function (btn) {
        btn.addEventListener("click", function () {
            var value = btn.getAttribute("data-filter");                // "all", "published" ou "draft"
            var shown = 0;                                              // nombre de lignes visibles

            filters.forEach(function (b) { b.classList.toggle("is-active", b === btn); });  // bouton actif en noir

            rows.forEach(function (row) {
                var match = value === "all" || row.getAttribute("data-status") === value;
                row.hidden = !match;                                    // cache les lignes qui ne correspondent pas
                if (match) {
                    row.classList.add("is-visible");                    // s'assure qu'elle est affichée (animation)
                    shown++;
                }
            });

            if (filterEmpty) filterEmpty.hidden = shown > 0;            // message si rien à afficher
        });
    });

    /* ----- Page "Écrire" : aperçu de l'image choisie ----- */
    var uploadInput = document.querySelector(".upload__input");        // champ fichier (caché)
    var uploadPreview = document.getElementById("uploadPreview");      // balise <img> d'aperçu

    if (uploadInput && uploadPreview) {
        uploadInput.addEventListener("change", function () {
            var file = uploadInput.files && uploadInput.files[0];       // fichier sélectionné
            if (!file) return;
            uploadPreview.src = URL.createObjectURL(file);              // affiche l'image sans l'envoyer
            uploadInput.closest(".upload").classList.add("has-image");  // cache le texte "Cliquer pour…"
        });
    }

    /* ----- Page "Écrire" : les zones de texte s'agrandissent en tapant ----- */
    document.querySelectorAll(".editor textarea").forEach(function (area) {
        var grow = function () {
            area.style.height = "auto";                                 // remet à zéro
            area.style.height = area.scrollHeight + "px";               // prend la hauteur du texte
        };
        area.addEventListener("input", grow);                           // à chaque frappe
        grow();                                                         // au chargement (mode modification)
    });

    /* =====================================================
       Page article : likes et commentaires façon TikTok
       ===================================================== */
    var csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");   // jeton de sécurité de la page
    var toastEl = document.getElementById("toast");                         // petit message temporaire
    var toastTimer;

    // Affiche un petit message en bas de l'écran pendant 2 secondes.
    function toast(message) {
        if (!toastEl) return;
        toastEl.textContent = message;
        toastEl.classList.add("is-on");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () { toastEl.classList.remove("is-on"); }, 2000);
    }

    // Envoie une requête POST au serveur et renvoie la réponse JSON.
    // Si l'utilisateur n'est pas connecté (401), on l'envoie vers la page de connexion.
    function postJSON(url, body) {
        return fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfInput ? csrfInput.value : "",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: body || null
        }).then(function (res) {
            return res.json().then(function (data) {
                if (res.status === 401 && data.login_url) {
                    window.location.href = data.login_url;
                    throw new Error("login");
                }
                if (!res.ok) throw new Error(data.error || "Erreur");
                return data;
            });
        });
    }

    // Like / unlike sur un bouton cœur (article ou commentaire).
    function toggleLike(btn, forceLike) {
        if (btn.dataset.busy) return;                        // évite les doubles clics trop rapides
        if (forceLike && btn.classList.contains("is-liked")) return;   // double-clic image : ne retire jamais un like

        btn.dataset.busy = "1";
        var countEl = btn.querySelector(".like-count");
        var wasLiked = btn.classList.contains("is-liked");

        // Mise à jour immédiate de l'affichage (on corrige ensuite avec la réponse du serveur)
        btn.classList.toggle("is-liked", !wasLiked);
        btn.setAttribute("aria-pressed", String(!wasLiked));
        countEl.textContent = Math.max(0, parseInt(countEl.textContent, 10) + (wasLiked ? -1 : 1));
        btn.classList.remove("pop"); void btn.offsetWidth; btn.classList.add("pop");   // relance l'animation

        postJSON(btn.dataset.likeUrl)
            .then(function (data) {
                btn.classList.toggle("is-liked", data.liked);
                btn.setAttribute("aria-pressed", String(data.liked));
                countEl.textContent = data.count;
            })
            .catch(function (err) {
                if (err.message === "login") return;
                btn.classList.toggle("is-liked", wasLiked);     // annule en cas d'erreur
                countEl.textContent = Math.max(0, parseInt(countEl.textContent, 10) + (wasLiked ? 1 : -1));
                toast("Oups, réessaie dans un instant.");
            })
            .finally(function () { delete btn.dataset.busy; });
    }

    // Un seul écouteur pour tous les cœurs, même ceux ajoutés plus tard.
    document.addEventListener("click", function (e) {
        var btn = e.target.closest(".like-btn");
        if (btn) toggleLike(btn);
    });

    // Double-clic sur l'image : like + gros cœur animé.
    var cover = document.getElementById("cover");
    var postLike = document.getElementById("postLike");
    if (cover && postLike) {
        cover.addEventListener("dblclick", function () {
            var burst = cover.querySelector(".burst");
            burst.classList.remove("is-on"); void burst.offsetWidth; burst.classList.add("is-on");
            toggleLike(postLike, true);
        });
    }

    // Barre de progression de lecture (page article).
    var progressBar = document.getElementById("readProgress");
    var postEl = document.getElementById("lecture");
    if (progressBar && postEl) {
        var updateProgress = function () {
            var start = postEl.offsetTop;                                   // début de l'article
            var end = start + postEl.offsetHeight - window.innerHeight;     // fin de l'article
            var ratio = Math.min(1, Math.max(0, (window.scrollY - start + 120) / Math.max(1, end - start)));
            progressBar.style.transform = "scaleX(" + ratio + ")";          // remplit la barre de 0 à 100 %
        };
        window.addEventListener("scroll", function () { requestAnimationFrame(updateProgress); }, { passive: true });
        window.addEventListener("resize", updateProgress);
        updateProgress();
    }

    // Boutons Partager (barre TikTok + bas d'article) : partage natif sur mobile, sinon copie du lien.
    document.querySelectorAll("#shareBtn, [data-share]").forEach(function (shareBtn) {
        shareBtn.addEventListener("click", function () {
            if (navigator.share) {
                navigator.share({ title: document.title, url: location.href }).catch(function () {});
            } else if (navigator.clipboard) {
                navigator.clipboard.writeText(location.href).then(function () { toast("Lien copié, à toi de le partager !"); });
            }
        });
    });

    // ----- Ouverture / fermeture du panneau de commentaires -----
    var sheet = document.getElementById("commentSheet");
    var backdrop = document.getElementById("sheetBackdrop");

    function openSheet() {
        if (!sheet) return;
        backdrop.hidden = false;
        requestAnimationFrame(function () { backdrop.classList.add("is-on"); });
        sheet.classList.add("is-open");
        sheet.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";                       // bloque le scroll de la page
        var field = sheet.querySelector("textarea");
        if (field && window.matchMedia("(min-width: 900px)").matches) field.focus();
    }

    function closeSheet() {
        if (!sheet || !sheet.classList.contains("is-open")) return;
        sheet.classList.remove("is-open");
        sheet.setAttribute("aria-hidden", "true");
        backdrop.classList.remove("is-on");
        setTimeout(function () { backdrop.hidden = true; }, 350);
        document.body.style.overflow = "";
    }

    if (sheet) {
        document.querySelectorAll("[data-open-comments]").forEach(function (b) {
            b.addEventListener("click", openSheet);
        });
        backdrop.addEventListener("click", closeSheet);
        document.getElementById("sheetClose").addEventListener("click", closeSheet);
        document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeSheet(); });
        if (location.hash === "#commentaires") openSheet();            // ouvert directement après connexion

        // Glisser le panneau vers le bas pour le fermer (mobile)
        var startY = null;
        sheet.querySelector(".sheet__head").addEventListener("touchstart", function (e) { startY = e.touches[0].clientY; }, { passive: true });
        sheet.addEventListener("touchend", function (e) {
            if (startY !== null && e.changedTouches[0].clientY - startY > 80) closeSheet();
            startY = null;
        });
    }

    // ----- Envoi d'un commentaire sans recharger la page -----
    var commentForm = document.getElementById("commentForm");
    if (commentForm) {
        var field = commentForm.querySelector("textarea");
        var send = commentForm.querySelector(".sheet__send");
        var list = document.getElementById("commentList");
        var empty = document.getElementById("commentEmpty");

        // Active le bouton dès qu'il y a du texte, et agrandit la zone en tapant.
        field.addEventListener("input", function () {
            send.disabled = !field.value.trim();
            field.style.height = "auto";
            field.style.height = field.scrollHeight + "px";
        });

        // Entrée = envoyer ; Maj + Entrée = nouvelle ligne.
        field.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (!send.disabled) commentForm.requestSubmit();
            }
        });

        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();
            if (!field.value.trim()) return;
            send.disabled = true;

            postJSON(commentForm.action, new FormData(commentForm))
                .then(function (data) {
                    list.insertAdjacentHTML("afterbegin", data.html);          // ajoute le commentaire en haut
                    var added = list.firstElementChild;
                    added.classList.add("is-new");
                    if (empty) empty.hidden = true;
                    document.querySelectorAll(".comment-count").forEach(function (el) { el.textContent = data.count; });
                    var plural = document.getElementById("commentPlural");
                    if (plural) plural.textContent = data.count > 1 ? "s" : "";
                    field.value = "";
                    field.style.height = "auto";
                    sheet.querySelector(".sheet__body").scrollTop = 0;
                    toast("Commentaire publié !");
                })
                .catch(function (err) {
                    if (err.message !== "login") toast(err.message);
                    send.disabled = !field.value.trim();
                });
        });
    }

    /* ----- Apparition des éléments au scroll ----- */
    var items = document.querySelectorAll(".reveal");

    if (!("IntersectionObserver" in window) || reduceMotion) {
        items.forEach(function (el) { el.classList.add("is-visible"); });
        return;
    }

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    items.forEach(function (el) { observer.observe(el); });
})();
