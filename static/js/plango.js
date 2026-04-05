/* =============================================================
   Plan N'Go — JavaScript
   ============================================================= */

/* -------------------------------------------------------------
   Tabs (Auth page)
   ------------------------------------------------------------- */
function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName)
  })
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `panel-${tabName}`)
  })
  document.getElementById('form-messages')?.classList.remove('active')
}

/* -------------------------------------------------------------
   Password toggle
   ------------------------------------------------------------- */
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId)
  if (!input) return
  const isPassword = input.type === 'password'
  input.type = isPassword ? 'text' : 'password'
  btn.innerHTML = isPassword ? iconEyeOff() : iconEye()
}

function iconEye() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>`
}

function iconEyeOff() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
    <line x1="1" y1="1" x2="23" y2="23"/>
  </svg>`
}

/* -------------------------------------------------------------
   Avatar preview
   ------------------------------------------------------------- */
function previewAvatar(input) {
  if (!input.files || !input.files[0]) return
  const reader = new FileReader()
  reader.onload = e => {
    const img = document.getElementById('avatar-img')
    const icon = document.getElementById('avatar-icon')
    if (img) {
      img.src = e.target.result
      img.style.display = 'block'
    }
    if (icon) icon.style.display = 'none'
  }
  reader.readAsDataURL(input.files[0])
}

/* -------------------------------------------------------------
   Tag toggles (idiomas, meses)
   ------------------------------------------------------------- */
function toggleTag(btn, inputName) {
  btn.classList.toggle('active')
  const value = btn.dataset.value
  const hidden = document.querySelector(`input[name="${inputName}"][value="${value}"]`)
  if (hidden) {
    hidden.disabled = !btn.classList.contains('active')
  }
}

/* -------------------------------------------------------------
   Modal
   ------------------------------------------------------------- */
function openModal(modalId) {
  const modal = document.getElementById(modalId)
  if (modal) {
    modal.classList.add('open')
    document.body.style.overflow = 'hidden'
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId)
  if (modal) {
    modal.classList.remove('open')
    document.body.style.overflow = ''
  }
}

// Fechar modal ao clicar no backdrop
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open')
    document.body.style.overflow = ''
  }
})

// Fechar modal com ESC
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.open').forEach(modal => {
      modal.classList.remove('open')
      document.body.style.overflow = ''
    })
  }
})

/* -------------------------------------------------------------
   CSRF token helper (para requisições AJAX)
   ------------------------------------------------------------- */
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || document.cookie.split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1]
}

/* -------------------------------------------------------------
   Mensagens Django (auto-hide)
   ------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  const messages = document.querySelectorAll('.django-message')
  messages.forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.5s'
      msg.style.opacity = '0'
      setTimeout(() => msg.remove(), 500)
    }, 4000)
  })
})
