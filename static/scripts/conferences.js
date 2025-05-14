// conferences.js - SPA dynamique avec vues HTML partielles

const container = document.getElementById('spa-container');
const isChair = true; // Simulation : rôle utilisateur

function loadView(viewPath, callback) {
  fetch(viewPath)
    .then(res => res.text())
    .then(html => {
      container.innerHTML = html;
      if (callback) callback();
    });
}

function loadCreateConference() {
  if (!isChair) {
    container.innerHTML = '<p>Accès refusé : seuls les Chairs peuvent créer une conférence.</p>';
    return;
  }

  loadView('views/create-conference.html', () => {
    const form = document.getElementById('create-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const data = Object.fromEntries(formData);

      try {
        const res = await fetch('../conferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (res.ok) {
          alert('Conférence créée avec succès');
          window.location.hash = '#conferences';
        } else {
          alert('Erreur lors de la création');
        }
      } catch (err) {
        console.error(err);
        alert('Erreur réseau');
      }
    });
  });
}

function loadListConferences() {
  loadView('views/list-conferences.html', () => {
    const list = document.getElementById('conf-list');
    const addBtnContainer = document.getElementById('add-conf-container');

    // Bouton Ajouter (Chair uniquement)
    if (isChair) {
      const btn = document.createElement('button');
      btn.className = 'vc-btn primary';
      btn.innerText = 'Ajouter une Conférence';
      btn.onclick = () => window.location.hash = '#create';
      addBtnContainer.appendChild(btn);
    }

    // Chargement des conférences
    fetch('../conferences')
      .then(res => res.json())
      .then(data => {
        const loading = document.getElementById('loading-msg');
        if (loading) loading.remove();

        if (data.length === 0) {
          list.innerHTML = '<p>Aucune conférence trouvée.</p>';
          return;
        }

        data.forEach(conf => {
          const card = document.createElement('div');
          card.className = 'conference-card';

          card.innerHTML = `
            <h3>${conf.name}</h3>
            <p><strong>Date :</strong> ${conf.date}</p>
            <p><strong>Lieu :</strong> ${conf.location}</p>
          `;

          // Suppression (Chair uniquement)
          if (isChair) {
            const delBtn = document.createElement('button');
            delBtn.innerText = '🗑 Supprimer';
            delBtn.className = 'conf-delete-btn';
            delBtn.onclick = async () => {
              if (confirm(`Supprimer la conférence \"${conf.name}\" ?`)) {
                try {
                  const res = await fetch(`/conferences/${conf.id}`, {
                    method: 'DELETE'
                  });
                  if (res.ok) {
                    alert('Conférence supprimée');
                    loadListConferences();
                  } else {
                    alert('Erreur lors de la suppression');
                  }
                } catch (err) {
                  console.error(err);
                  alert('Erreur réseau');
                }
              }
            };
            card.appendChild(delBtn);
          }

          // Cliquez pour voir les détails
          card.addEventListener('click', () => {
            window.location.hash = `#conference/${conf.id}`;
          });

          list.appendChild(card);
        });
      });
  });
}

function loadHome() {
  loadView('views/home.html');
}

function routeFromHash() {
  const hash = window.location.hash;
  if (hash === '#conferences') {
    loadListConferences();
  } else if (hash === '#create') {
    loadCreateConference();
  } else {
    loadHome();
  }
}

window.addEventListener('hashchange', routeFromHash);
window.addEventListener('DOMContentLoaded', routeFromHash);

function loadHome() {
    loadView('views/home.html');
  }