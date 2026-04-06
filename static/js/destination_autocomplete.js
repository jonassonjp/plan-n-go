/* =============================================================
   Plan N'Go — Autocomplete de Destinos
   Ao selecionar um lugar, preenche país, continente e idiomas.
   ============================================================= */

(function () {
  "use strict";

  const DEBOUNCE_MS = 400;
  const MIN_CHARS   = 2;

  // Mapeamento país → idiomas principais
  const COUNTRY_LANGUAGES = {
    "BR": ["Português"],
    "PT": ["Português"],
    "US": ["Inglês"],
    "GB": ["Inglês"],
    "AU": ["Inglês"],
    "CA": ["Inglês", "Francês"],
    "FR": ["Francês"],
    "BE": ["Francês", "Holandês"],
    "CH": ["Francês", "Alemão", "Italiano"],
    "DE": ["Alemão"],
    "AT": ["Alemão"],
    "IT": ["Italiano"],
    "ES": ["Espanhol"],
    "MX": ["Espanhol"],
    "AR": ["Espanhol"],
    "CL": ["Espanhol"],
    "CO": ["Espanhol"],
    "PE": ["Espanhol"],
    "BO": ["Espanhol"],
    "PY": ["Espanhol"],
    "UY": ["Espanhol"],
    "VE": ["Espanhol"],
    "EC": ["Espanhol"],
    "CR": ["Espanhol"],
    "PA": ["Espanhol"],
    "DO": ["Espanhol"],
    "GT": ["Espanhol"],
    "HN": ["Espanhol"],
    "SV": ["Espanhol"],
    "NI": ["Espanhol"],
    "CU": ["Espanhol"],
    "JP": ["Japonês"],
    "CN": ["Mandarim"],
    "TW": ["Mandarim"],
    "KR": ["Coreano"],
    "SA": ["Árabe"],
    "AE": ["Árabe"],
    "EG": ["Árabe"],
    "MA": ["Árabe"],
    "IN": ["Hindi", "Inglês"],
    "RU": ["Russo"],
    "UA": ["Russo"],
    "GR": ["Grego"],
    "NL": ["Holandês"],
    "SE": ["Sueco"],
    "TH": ["Tailandês"],
    "VN": ["Vietnamita"],
    "ID": ["Indonésio"],
    "MY": ["Indonésio", "Inglês"],
  };

  let debounceTimer  = null;
  let activeIndex    = -1;
  let currentResults = [];

  const nameInput     = document.getElementById("dest-name");
  const dropdown      = document.getElementById("dest-autocomplete");
  const countryInput  = document.getElementById("dest-country");
  const continentHint = document.getElementById("dest-continent-hint");
  const continentHid  = document.getElementById("dest-continent");
  const latInput      = document.getElementById("dest-lat");
  const lonInput      = document.getElementById("dest-lon");
  const placeIdInput  = document.getElementById("dest-place-id");

  if (!nameInput || !dropdown) return;

  // Eventos do input de nome
  nameInput.addEventListener("input", () => {
    const query = nameInput.value.trim();
    clearTimeout(debounceTimer);
    resetSelection();
    if (query.length < MIN_CHARS) { hideDropdown(); return; }
    debounceTimer = setTimeout(() => fetchSuggestions(query), DEBOUNCE_MS);
  });

  nameInput.addEventListener("keydown", (e) => {
    if (!dropdown.classList.contains("dest-autocomplete--open")) return;
    if (e.key === "ArrowDown")  { e.preventDefault(); moveFocus(1); }
    else if (e.key === "ArrowUp")   { e.preventDefault(); moveFocus(-1); }
    else if (e.key === "Enter") { e.preventDefault(); if (activeIndex >= 0) selectSuggestion(currentResults[activeIndex]); }
    else if (e.key === "Escape") hideDropdown();
  });

  document.addEventListener("click", (e) => {
    if (!nameInput.contains(e.target) && !dropdown.contains(e.target)) hideDropdown();
  });

  async function fetchSuggestions(query) {
    showLoading();
    try {
      const res  = await fetch(`/destinations/autocomplete/?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      currentResults = data.suggestions || [];
      renderDropdown(currentResults);
    } catch { hideDropdown(); }
  }

  function renderDropdown(suggestions) {
    dropdown.innerHTML = "";
    if (!suggestions.length) {
      dropdown.innerHTML = `<div class="dest-autocomplete__empty">Nenhum resultado encontrado</div>`;
      showDropdown(); return;
    }
    suggestions.forEach((s, i) => {
      const item = document.createElement("button");
      item.type  = "button";
      item.className = "dest-autocomplete__item";
      item.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        <span class="dest-autocomplete__item-name">${escapeHtml(s.name)}</span>
        <span class="dest-autocomplete__item-sub">${escapeHtml(s.country)}${s.continent ? " · " + s.continent : ""}</span>`;
      item.addEventListener("mousedown", (e) => {
        e.preventDefault(); // evita blur no input antes do clique
        selectSuggestion(s);
      });
      dropdown.appendChild(item);
    });
    showDropdown();
  }

  function selectSuggestion(s) {
    nameInput.value = s.name;

    if (countryInput)  countryInput.value  = s.country  || "";
    if (continentHid)  continentHid.value  = s.continent || "";
    if (latInput)      latInput.value      = s.lat      || "";
    if (lonInput)      lonInput.value      = s.lon      || "";
    if (placeIdInput)  placeIdInput.value  = s.place_id || "";

    // Hint do continente
    if (continentHint && s.continent) {
      continentHint.textContent = `Continente: ${s.continent}`;
      continentHint.style.display = "block";
    }

    // Preencher idiomas automaticamente
    const countryCode = (s.country_code || "").toUpperCase();
    const langs = COUNTRY_LANGUAGES[countryCode] || [];
    if (langs.length > 0) selectLanguages(langs);

    hideDropdown();
    nameInput.focus();
  }

  function selectLanguages(langs) {
    // Desativa todos
    document.querySelectorAll(".tag-btn").forEach(btn => {
      btn.classList.remove("tag-btn--active");
      const cb = btn.nextElementSibling;
      if (cb && cb.type === "checkbox") cb.disabled = true;
    });
    // Ativa os do país
    langs.forEach(lang => {
      const btn = document.querySelector(`.tag-btn[data-value="${lang}"]`);
      if (btn) {
        btn.classList.add("tag-btn--active");
        const cb = btn.nextElementSibling;
        if (cb && cb.type === "checkbox") cb.disabled = false;
      }
    });
  }

  function moveFocus(dir) {
    const items = dropdown.querySelectorAll(".dest-autocomplete__item");
    if (!items.length) return;
    items[activeIndex]?.classList.remove("dest-autocomplete__item--active");
    activeIndex = Math.max(-1, Math.min(items.length - 1, activeIndex + dir));
    items[activeIndex]?.classList.add("dest-autocomplete__item--active");
  }

  function resetSelection() {
    activeIndex = -1;
    dropdown.querySelectorAll(".dest-autocomplete__item--active")
      .forEach(el => el.classList.remove("dest-autocomplete__item--active"));
  }

  function showDropdown() { dropdown.classList.add("dest-autocomplete--open"); }
  function hideDropdown()  {
    dropdown.classList.remove("dest-autocomplete--open");
    dropdown.innerHTML = "";
    activeIndex = -1;
  }

  function showLoading() {
    dropdown.innerHTML = `
      <div class="dest-autocomplete__loading">
        <span class="dest-autocomplete__spinner"></span>
        Buscando...
      </div>`;
    showDropdown();
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

})();
