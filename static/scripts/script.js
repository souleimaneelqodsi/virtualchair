const container = document.getElementById("spa-container");
const loginBtn = document.getElementById("login-btn");
const logoutBtn = document.getElementById("logout-btn");
const heroContent = document.querySelector(".hero-content");

function loadView(viewPath, callback) {
    fetch(viewPath)
        .then((res) => res.text())
        .then((html) => {
            container.innerHTML = html;
            if (callback) callback();
        });
}

function loadHome() {
    loadView("views/home.html", () => {
        updateHeaderLinks();
    });
}

function loadCreateConference() {
    loadView("views/create-conference.html", () => {
        const form = document.getElementById("create-form");
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            try {
                const res = await fetch("/api/conferences", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        // Include Authorization header if your API requires JWT for this endpoint
                        // "Authorization": `Bearer ${localStorage.getItem("token")}`
                    },
                    body: JSON.stringify(data),
                });

                const result = await res.json();
                if (res.ok) {
                    alert("Conférence créée avec succès");
                    window.location.hash = "#conferences";
                } else {
                    alert(
                        result.error ||
                            result.message ||
                            "Erreur lors de la création",
                    );
                }
            } catch (err) {
                console.error(err);
                alert("Erreur réseau");
            }
        });
    });
}

function loadListConferences() {
    loadView("views/list-conferences.html", () => {
        const list = document.getElementById("conf-list");
        const addBtnContainer = document.getElementById("add-conf-container");
        addBtnContainer.innerHTML = ""; // Clear previous button

        const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
        if (isLoggedIn) {
            // Only show add button if logged in
            const btn = document.createElement("button");
            btn.className = "vc-btn primary";
            btn.innerText = "Ajouter une Conférence";
            btn.onclick = () => (window.location.hash = "#create");
            addBtnContainer.appendChild(btn);
        }

        fetch("/api/conferences")
            .then((res) =>
                res.json().then((data) => ({ status: res.status, body: data })),
            )
            .then(({ status, body }) => {
                list.innerHTML = "";

                if (status !== 200) {
                    list.innerHTML = `<p style="color:red;text-align:center">${body.message || body.error || "Erreur lors du chargement des conférences."}</p>`;
                    return;
                }

                if (!Array.isArray(body) || body.length === 0) {
                    list.innerHTML =
                        '<p style="text-align:center; color:#888">Aucune conférence disponible pour le moment.</p>';
                    return;
                }

                body.forEach((conf) => {
                    const card = document.createElement("div");
                    card.className = "conference-card";

                    card.innerHTML = `
                        <h3>${conf.name}</h3>
                        <p><strong>Date de début :</strong> ${conf.start_date || "N/A"}</p>
                        <p><strong>Lieu :</strong> ${conf.location || "N/A"}</p>
                        <p><strong>Phase :</strong> ${conf.current_phase || "N/A"}</p>
                    `;

                    // Add delete button only if the current user is the creator (example logic)
                    // This requires creator_id to be part of the conference list response
                    // and current user ID to be available.
                    // For simplicity, I'll omit the delete button logic here as it wasn't the focus.

                    card.addEventListener("click", () => {
                        window.location.hash = `#conference/${conf.id}`;
                    });

                    list.appendChild(card);
                });
            })
            .catch((err) => {
                console.error(err);
                list.innerHTML =
                    '<p style="text-align:center; color:#c00">Impossible de charger les conférences. Veuillez réessayer plus tard.</p>';
            });
    });
}

async function loadConferenceDetail(conferenceId) {
    loadView("views/detail-conference.html", async () => {
        const detailDiv = document.getElementById("conference-detail");
        const submissionSectionDiv = document.getElementById(
            "paper-submission-section",
        );
        const papersListDiv = document.getElementById("papers-list");

        detailDiv.innerHTML =
            "<p>Chargement des détails de la conférence...</p>";
        submissionSectionDiv.innerHTML = ""; // Clear previous form
        papersListDiv.innerHTML = "<p>Chargement des papiers soumis...</p>";

        const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
        const currentUserId = localStorage.getItem("id");

        try {
            // 1. Fetch conference details
            const confRes = await fetch(`/api/conferences/${conferenceId}`);
            const confData = await confRes.json();

            if (!confRes.ok) {
                detailDiv.innerHTML = `<p style="color:red;text-align:center">${confData.error || confData.message || "Erreur lors du chargement de la conférence."}</p>`;
                papersListDiv.innerHTML = ""; // Don't show papers if conference fails to load
                return;
            }

            detailDiv.innerHTML = `
                <h3>${confData.name}</h3>
                <p><strong>Description :</strong> ${confData.description || "N/A"}</p>
                <p><strong>Date de début :</strong> ${confData.start_date || "N/A"}</p>
                <p><strong>Date de fin :</strong> ${confData.end_date || "N/A"}</p>
                <p><strong>Lieu :</strong> ${confData.location || "N/A"}</p>
                <p><strong>Deadline Soumission :</strong> ${confData.submission_deadline || "N/A"}</p>
                <p><strong>Phase Actuelle :</strong> ${confData.current_phase || "N/A"}</p>
            `;

            // 2. Fetch user roles for this conference (if logged in)
            let canSubmit = false;
            if (isLoggedIn && currentUserId) {
                try {
                    const rolesRes = await fetch(
                        `/api/conferences/${conferenceId}/my-roles`,
                    );
                    if (rolesRes.ok) {
                        const rolesData = await rolesRes.json();
                        const userRoles = rolesData.roles || [];
                        if (
                            !userRoles.includes("Chair") &&
                            !userRoles.includes("Reviewer")
                        ) {
                            canSubmit = true;
                        } else {
                            submissionSectionDiv.innerHTML =
                                "<p><em>Vous ne pouvez pas soumettre de papier à cette conférence car vous êtes Chair ou Reviewer.</em></p>";
                        }
                    } else {
                        submissionSectionDiv.innerHTML =
                            "<p><em>Impossible de vérifier vos droits de soumission.</em></p>";
                    }
                } catch (roleError) {
                    console.error("Error fetching user roles:", roleError);
                    submissionSectionDiv.innerHTML =
                        "<p><em>Erreur lors de la vérification des droits de soumission.</em></p>";
                }
            } else if (!isLoggedIn) {
                submissionSectionDiv.innerHTML =
                    "<p><em>Veuillez vous connecter pour soumettre un papier.</em></p>";
            }

            if (canSubmit) {
                submissionSectionDiv.innerHTML = `
                    <h4>Soumettre un nouveau papier</h4>
                    <form id="submit-paper-form" class="spa-form">
                        <input type="text" name="title" placeholder="Titre du papier" required />
                        <textarea name="abstract" placeholder="Résumé (optionnel)"></textarea>
                        <input type="text" name="keywords" placeholder="Mots-clés (séparés par des virgules, optionnel)" />
                        <input type="file" name="file" accept=".pdf,.doc,.docx,.txt" required />
                        <button type="submit">Soumettre le Papier</button>
                    </form>
                `;
                const paperForm = document.getElementById("submit-paper-form");
                paperForm.addEventListener("submit", async (e) => {
                    e.preventDefault();
                    const formData = new FormData(paperForm);
                    // conferenceId is already available in the scope
                    // authorId is currentUserId

                    try {
                        const submitRes = await fetch(
                            `/api/conferences/${conferenceId}/papers`,
                            {
                                method: "POST",
                                // Headers are not 'application/json' for FormData
                                // "Authorization": `Bearer ${localStorage.getItem("token")}` // If needed
                                body: formData,
                            },
                        );
                        const submitResult = await submitRes.json();
                        if (submitRes.ok) {
                            alert("Papier soumis avec succès !");
                            paperForm.reset();
                            fetchSubmittedPapers(conferenceId, papersListDiv); // Refresh list
                        } else {
                            alert(
                                submitResult.error ||
                                    submitResult.message ||
                                    "Erreur lors de la soumission du papier.",
                            );
                        }
                    } catch (submitErr) {
                        console.error("Paper submission error:", submitErr);
                        alert("Erreur réseau lors de la soumission.");
                    }
                });
            }

            // 3. Fetch and display submitted papers for this conference
            fetchSubmittedPapers(conferenceId, papersListDiv);
        } catch (error) {
            console.error("Error loading conference details:", error);
            detailDiv.innerHTML = `<p style="color:red;text-align:center">Une erreur majeure est survenue.</p>`;
            papersListDiv.innerHTML = "";
        }
    });
}

async function fetchSubmittedPapers(conferenceId, papersListDiv) {
    papersListDiv.innerHTML = "<p>Chargement des papiers...</p>";
    try {
        const papersRes = await fetch(
            `/api/conferences/${conferenceId}/papers`,
        );
        const papersData = await papersRes.json();

        if (!papersRes.ok) {
            papersListDiv.innerHTML = `<p style="color:red;">${papersData.error || papersData.message || "Erreur chargement des papiers."}</p>`;
            return;
        }

        if (!Array.isArray(papersData) || papersData.length === 0) {
            papersListDiv.innerHTML =
                "<p>Aucun papier soumis pour le moment.</p>";
            return;
        }

        papersListDiv.innerHTML = ""; // Clear loading message
        const ul = document.createElement("ul");
        ul.className = "papers-submitted-list";
        papersData.forEach((paper) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <strong>${paper.title}</strong> (Statut: ${paper.status})
                <br>
                <small>Soumis le: ${new Date(paper.submitted_at).toLocaleDateString()}</small>
                ${paper.s3_file_url ? `<br><a href="${paper.s3_file_url}" target="_blank" rel="noopener noreferrer">Voir Fichier</a>` : ""}
            `;
            // Potentially add a link to paper detail view: <a href="#conference/${conferenceId}/paper/${paper.id}">Voir Détails</a>
            ul.appendChild(li);
        });
        papersListDiv.appendChild(ul);
    } catch (error) {
        console.error("Error fetching submitted papers:", error);
        papersListDiv.innerHTML =
            "<p style='color:red;'>Impossible de charger la liste des papiers.</p>";
    }
}

function loadLogin() {
    loadView("views/login.html", () => {
        const form = document.getElementById("login-form");
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            try {
                const res = await fetch("/api/users/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });

                const result = await res.json();
                if (res.ok) {
                    localStorage.setItem("isLoggedIn", "true");
                    localStorage.setItem("username", result.username);
                    localStorage.setItem("email", result.email);
                    localStorage.setItem("id", result.id);
                    // localStorage.setItem("token", result.token); // If you implement JWT
                    alert("Connexion réussie");
                    updateHeaderLinks();
                    window.location.hash = "#home";
                } else {
                    alert(result.error || "Erreur de connexion");
                }
            } catch (err) {
                console.error(err);
                alert("Erreur réseau");
            }
        });
    });
}

function loadRegister() {
    loadView("views/register.html", () => {
        const form = document.getElementById("register-form");
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            try {
                const res = await fetch("/api/users/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });

                const result = await res.json();
                if (res.ok) {
                    localStorage.setItem("isLoggedIn", "true");
                    localStorage.setItem("username", result.username);
                    localStorage.setItem("email", result.email);
                    localStorage.setItem("id", result.id);
                    // localStorage.setItem("token", result.token); // If you implement JWT
                    alert("Inscription réussie");
                    updateHeaderLinks();
                    window.location.hash = "#home";
                } else {
                    alert(result.error || "Erreur lors de l’inscription");
                }
            } catch (err) {
                console.error(err);
                alert("Erreur réseau");
            }
        });
    });
}

async function logoutUser() {
    try {
        const res = await fetch("/api/users/logout", {
            method: "POST",
            // headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` } // If needed
        });

        const result = await res.json();

        if (res.ok) {
            localStorage.removeItem("isLoggedIn");
            localStorage.removeItem("username");
            localStorage.removeItem("email");
            localStorage.removeItem("id");
            // localStorage.removeItem("token");
            alert(result.message || "Déconnexion réussie");
            updateHeaderLinks();
            window.location.hash = "#login";
        } else {
            alert(
                result.error ||
                    result.message ||
                    "Erreur lors de la déconnexion",
            );
        }
    } catch (err) {
        console.error(err);
        alert("Erreur réseau lors de la déconnexion");
    }
}

function updateHeaderLinks() {
    const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
    const homeRegisterCTA = document.getElementById("home-register-cta");

    if (isLoggedIn) {
        if (loginBtn) loginBtn.style.display = "none";
        if (logoutBtn) logoutBtn.style.display = "block";
        if (heroContent) heroContent.style.display = "none";
        if (homeRegisterCTA) homeRegisterCTA.style.display = "none";
    } else {
        if (loginBtn) loginBtn.style.display = "block";
        if (logoutBtn) logoutBtn.style.display = "none";
        if (heroContent) heroContent.style.display = "block";
        if (homeRegisterCTA) homeRegisterCTA.style.display = "block";
    }
}

function routeFromHash() {
    const hash = window.location.hash;

    if (hash === "#conferences") {
        loadListConferences();
    } else if (hash === "#create") {
        loadCreateConference();
    } else if (hash.startsWith("#conference/")) {
        const id = hash.split("/")[1];
        loadConferenceDetail(id);
    } else if (hash === "#login") {
        loadLogin();
    } else if (hash === "#register") {
        loadRegister();
    } else {
        loadHome();
        return;
    }
    updateHeaderLinks();
}

window.addEventListener("hashchange", routeFromHash);

window.addEventListener("DOMContentLoaded", () => {
    routeFromHash();
});

if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        logoutUser();
    });
}
