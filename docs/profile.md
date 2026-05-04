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
| Nome completo  | Não         | Nome real do usuário (`user.name`)                            |
| E-mail         | Não         | Alteração segura com confirmação por token (ver abaixo)       |
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
- **Redefinir senha**: card estilizado abaixo dos botões redireciona para `/accounts/password-reset/`
- **Troca de e-mail**: ao informar um novo e-mail, o sistema envia uma confirmação para o novo endereço. O e-mail atual permanece ativo até a confirmação via token UUID (`/accounts/email-change/confirm/<token>/`). Enquanto pendente, o campo exibe aviso amarelo com o e-mail aguardando confirmação.

---

## Fluxo de troca de e-mail

1. Usuário edita o campo **E-mail** no formulário de perfil
2. Sistema valida que o novo e-mail não está em uso
3. Salva `user.pending_email` e `user.email_change_token`
4. Envia e-mail de confirmação para o novo endereço via `_send_email_change_confirmation()`
5. Usuário clica no link → `confirm_email_change_view` valida token e efetiva a troca
6. `user.email` é atualizado; `pending_email` e `email_change_token` são limpos

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
