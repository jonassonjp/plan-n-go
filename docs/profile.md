# Perfil do Usuário

## Visão geral

Após confirmar o e-mail, o usuário é redirecionado para a página de perfil.  
Esta página faz parte do sistema (tem navbar, boas-vindas, indicador de progresso).

---

## URL

```
GET/POST /accounts/profile/setup/
```

---

## Campos do perfil

| Campo          | Obrigatório | Descrição                                                     |
|----------------|-------------|---------------------------------------------------------------|
| Foto de perfil | Não         | Upload de imagem. Aparece na navbar e em roteiros públicos    |
| Nome público   | Não         | Como o usuário quer ser chamado. Se vazio, usa nome completo  |
| Nacionalidade  | Não         | Usado para sugerir informações de visto automaticamente       |

---

## Indicador de progresso

A tela exibe 4 etapas:

```
✓ Cadastro → ✓ E-mail confirmado → ● Perfil → ○ Explorar
```

---

## Comportamento

- **Pular**: botão "Pular por agora" submete o formulário com `skip=1`  
  → redireciona para o dashboard sem salvar alterações
- **Salvar**: preenche os campos e clica "Salvar e começar"  
  → salva e redireciona para o dashboard
- **Nome público vazio**: property `public_name` retorna o nome completo automaticamente

---

## Navbar do sistema

A navbar das páginas internas (`components/app_navbar.html`) exibe:

- Logo Plan N'Go (link para landing page)
- Link "Meus Destinos"
- Avatar com iniciais (ou foto) + nome do usuário → link para o perfil
- Botão "Sair"

As iniciais são geradas pela property `user.initials`:

```python
# Jonas Pereira → JP
# Jonas → JO
```
