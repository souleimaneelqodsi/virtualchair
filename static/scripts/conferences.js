// conferences.js - SPA dynamique avec vues HTML partielles

const container = document.getElementById('spa-container');

function loadView(viewPath, callback) {
  fetch(viewPath)
    .then(res => res.text())
    .then(html => {
      container.innerHTML = html;
      if (callback) callback();
    });
}

function loadHome() {
  loadView('views/home.html');
}

function loadCreateConference() {
  loadView('views/create-conference.html', () => {
    const form = document.getElementById('create-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const data = Object.fromEntries(formData);

      try {
        const res = await fetch('/api/conferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });

        const result = await res.json();
        if (res.ok) {
          alert('Conférence créée avec succès');
          window.location.hash = '#conferences';
        } else {
          alert(result.message || 'Erreur lors de la création');
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

    const btn = document.createElement('button');
    btn.className = 'vc-btn primary';
    btn.innerText = 'Ajouter une Conférence';
    btn.onclick = () => window.location.hash = '#create';
    addBtnContainer.appendChild(btn);

    fetch('/api/conferences')
      .then(res => res.json().then(data => ({ status: res.status, body: data })))
      .then(({ status, body }) => {
        list.innerHTML = '';

        if (status !== 200) {
          list.innerHTML = `<p style="color:red;text-align:center">${body.message || 'Erreur lors du chargement des conférences.'}</p>`;
          return;
        }

        if (!Array.isArray(body) || body.length === 0) {
          list.innerHTML = '<p style="text-align:center; color:#888">Aucune conférence disponible pour le moment.</p>';
          return;
        }

        body.forEach(conf => {
          const card = document.createElement('div');
          card.className = 'conference-card';

          card.innerHTML = `
            <h3>${conf.name}</h3>
            <p><strong>Date :</strong> ${conf.date}</p>
            <p><strong>Lieu :</strong> ${conf.location}</p>
          `;

          const delBtn = document.createElement('button');
          delBtn.innerText = '🗑 Supprimer';
          delBtn.className = 'conf-delete-btn';
          delBtn.onclick = async (e) => {
            e.stopPropagation();
            if (confirm(`Supprimer la conférence \"${conf.name}\" ?`)) {
              try {
                const res = await fetch(`/api/conferences/${conf.id}`, {
                  method: 'DELETE'
                });
                const msg = await res.json();
                if (res.ok) {
                  alert('Conférence supprimée');
                  loadListConferences();
                } else {
                  alert(msg.message || 'Erreur lors de la suppression');
                }
              } catch (err) {
                console.error(err);
                alert('Erreur réseau');
              }
            }
          };
          card.appendChild(delBtn);

          card.addEventListener('click', () => {
            window.location.hash = `#conference/${conf.id}`;
          });

          list.appendChild(card);
        });
      })
      .catch(err => {
        console.error(err);
        list.innerHTML = '<p style="text-align:center; color:#c00">Impossible de charger les conférences. Veuillez réessayer plus tard.</p>';
      });
  });
}

function loadConferenceDetail(id) {
  loadView('views/detail-conference.html', () => {
    const detail = document.getElementById('conference-detail');

    fetch(`/api/conferences/${id}`)
      .then(res => res.json().then(data => ({ status: res.status, body: data })))
      .then(({ status, body }) => {
        if (status !== 200) {
          detail.innerHTML = `<p style="color:red;text-align:center">${body.message || 'Erreur lors du chargement de la conférence.'}</p>`;
          return;
        }

        detail.innerHTML = `
          <h3>${body.name}</h3>
          <p><strong>Date :</strong> ${body.date}</p>
          <p><strong>Lieu :</strong> ${body.location}</p>
          <a href="#conferences" class="vc-btn primary">&larr; Retour</a>
        `;
      })
      .catch(err => {
        console.error(err);
        detail.innerHTML = '<p style="text-align:center; color:#c00">Impossible de charger les détails de la conférence.</p>';
      });
  });
}

function routeFromHash() {
  const hash = window.location.hash;

  if (hash === '#conferences') {
    loadListConferences();
  } else if (hash === '#create') {
    loadCreateConference();
  } else if (hash.startsWith('#conference/')) {
    const id = hash.split('/')[1];
    loadConferenceDetail(id);
  } else {
    loadHome();
  }
}

window.addEventListener('hashchange', routeFromHash);
window.addEventListener('DOMContentLoaded', routeFromHash);

window.addEventListener('DOMContentLoaded', routeFromHash);

function loadHome() {
    loadView('views/home.html');
  }