/* =============================================================
   Plan N'Go — Autocomplete de Destinos
   Usa o endpoint Django /destinations/autocomplete/?q=...
   ============================================================= */

(function () {
  "use strict";

  const DEBOUNCE_MS   = 400;
  const MIN_CHARS     = 2;
  const CSRF_TOKEN    = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

  // -------------------------------------------------------
  // Estado
  // -------------------------------------------------------
  let debounceTimer   = null;
  let activeIndex     = -1;
  let currentResults  = [];

  // -------------------------------------------------------
  // Elementos DOM
  // -------------------------------------------------------
  const nameInput     = document.getElementById("dest-name");
  const dropdown      = document.getElementById("dest-autocomplete");
  const countryInput  = document.getElementById("dest-country");
  const continentHint = document.getElementById("dest-continent-hint");
  const latInput      = document.getElementById("dest-lat");
  const lonInput      = document.getElementById("dest-lon");
  const placeIdInput  = document.getElementById("dest-place-id");

  if (!nameInput || !dropdown) return;

  // -------------------------------------------------------
  // Eventos do input
  // -------------------------------------------------------
  nameInput.addEventListener("input", () => {
    const query = nameInput.value.trim();

    clearTimeout(debounceTimer);
    resetSelection();

    if (query.length < MIN_CHARS) {
      hideDropdown();
      return;
    }

    debounceTimer = setTimeout(() => fetchSuggestions(query), DEBOUNCE_MS);
  });

  nameInput.addEventListener("keydown", (e) => {
    if (!dropdown.classList.contains("dest-autocomplete--open")) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      moveFocus(1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      moveFocus(-1);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIndex >= 0) selectSuggestion(currentResults[activeIndex]);
    } else if (e.key === "Escape") {
      hideDropdown();
    }
  });

  // Fechar ao clicar fora
  document.addEventListener("click", (e) => {
    if (!nameInput.contains(e.target) && !dropdown.contains(e.target)) {
      hideDropdown();
    }
  });

  // -------------------------------------------------------
  // Busca sugestões no backend Django
  // -------------------------------------------------------
  async function fetchSuggestions(query) {
    showLoading();

    try {
      const res  = await fetch(`/destinations/autocomplete/?q=${encodeURIComponent(query)}`, {
        headers: { "X-CSRFToken": CSRF_TOKEN },
      });
      const data = await res.json();
      currentResults = data.suggestions || [];
      renderDropdown(currentResults);
    } catch {
      hideDropdown();
    }
  }

  // -------------------------------------------------------
  // Renderiza o dropdown
  // -------------------------------------------------------
  function renderDropdown(suggestions) {
    dropdown.innerHTML = "";

    if (!suggestions.length) {
      dropdown.innerHTML = `
        <div class="dest-autocomplete__empty">
          Nenhum resultado encontrado
        </div>`;
      showDropdown();
      return;
    }

    suggestions.forEach((s, i) => {
      const item = document.createElement("button");
      item.type  = "button";
      item.className = "dest-autocomplete__item";
      item.dataset.index = i;
      item.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        <span class="dest-autocomplete__item-name">${escapeHtml(s.name)}</span>
        <span class="dest-autocomplete__item-sub">${escapeHtml(s.country)}${s.continent ? " · " + s.continent : ""}</span>
      `;
      item.addEventListener("click", () => selectSuggestion(s));
      dropdown.appendChild(item);
    });

    showDropdown();
  }

  // -------------------------------------------------------
  // Seleciona uma sugestão e preenche os campos
  // -------------------------------------------------------
  function selectSuggestion(s) {
    nameInput.value = s.name;

    if (countryInput)  countryInput.value  = s.country  || "";
    if (latInput)      latInput.value      = s.lat      || "";
    if (lonInput)      lonInput.value      = s.lon      || "";
    if (placeIdInput)  placeIdInput.value  = s.place_id || "";

    if (continentHint && s.continent) {
      continentHint.textContent = `Continente detectado: ${s.continent}`;
      continentHint.style.display = "block";
    }

    hideDropdown();
    nameInput.focus();
  }

  // -------------------------------------------------------
  // Navegação por teclado
  // -------------------------------------------------------
  function moveFocus(direction) {
    const items = dropdown.querySelectorAll(".dest-autocomplete__item");
    if (!items.length) return;

    items[activeIndex]?.classList.remove("dest-autocomplete__item--active");
    activeIndex = Math.max(-1, Math.min(items.length - 1, activeIndex + direction));
    items[activeIndex]?.classList.add("dest-autocomplete__item--active");
  }

  function resetSelection() {
    activeIndex = -1;
    dropdown.querySelectorAll(".dest-autocomplete__item--active")
      .forEach(el => el.classList.remove("dest-autocomplete__item--active"));
  }

  // -------------------------------------------------------
  // Mostrar / esconder dropdown
  // -------------------------------------------------------
  function showDropdown() {
    dropdown.classList.add("dest-autocomplete--open");
  }

  function hideDropdown() {
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

  // -------------------------------------------------------
  // Utilitários
  // -------------------------------------------------------
  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

})();
