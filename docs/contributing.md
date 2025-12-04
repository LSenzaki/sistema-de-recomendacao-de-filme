# Guia de Contribuição

Obrigado por considerar contribuir para o Sistema de Recomendação de Filmes! 🎉

## Código de Conduta

Ao participar deste projeto, você concorda em manter um ambiente respeitoso e inclusivo para todos.

### Nossas Expectativas

- ✅ Seja respeitoso e inclusivo
- ✅ Aceite críticas construtivas
- ✅ Foque no que é melhor para a comunidade
- ✅ Mostre empatia com outros membros

## Como Contribuir

### Reportando Bugs 🐛

Se você encontrou um bug, por favor:

1. **Verifique** se o bug já foi reportado nas [Issues](https://github.com/seu-usuario/sistema-de-recomendacao-de-filme/issues)
2. **Crie uma nova issue** com:
   - Título descritivo
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Screenshots (se aplicável)
   - Ambiente (OS, Python version, etc.)

**Template de Bug Report**:

```markdown
**Descrição do Bug**
Descrição clara do problema.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente**
- OS: [e.g. Windows 11]
- Python: [e.g. 3.10]
- Browser: [e.g. Chrome 120]
```

### Sugerindo Features ✨

Tem uma ideia para melhorar o projeto?

1. **Verifique** se já não foi sugerido
2. **Crie uma issue** com:
   - Descrição clara da feature
   - Por que seria útil
   - Exemplos de uso
   - Possível implementação (opcional)

**Template de Feature Request**:

```markdown
**Descrição da Feature**
Descrição clara da funcionalidade proposta.

**Problema que Resolve**
Qual problema esta feature resolve?

**Solução Proposta**
Como você imagina que funcione?

**Alternativas Consideradas**
Outras abordagens que você considerou?
```

### Contribuindo com Código 💻

#### Configuração do Ambiente

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/seu-usuario/sistema-de-recomendacao-de-filme.git
   cd sistema-de-recomendacao-de-filme
   ```

3. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

4. **Instale dependências**:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r requirements-docs.txt
   ```

5. **Crie uma branch**:
   ```bash
   git checkout -b feature/minha-feature
   ```

#### Padrões de Código

##### Python (Backend)

**Estilo**: Seguimos [PEP 8](https://pep8.org/)

```python
# Bom ✅
def calculate_similarity(query: str, movies: pd.DataFrame) -> List[Dict]:
    """
    Calculate similarity between query and movies.
    
    Args:
        query: Search query string
        movies: DataFrame with movie data
        
    Returns:
        List of movies with similarity scores
    """
    # Implementation
    pass

# Ruim ❌
def calc(q,m):
    # No docstring, unclear names
    pass
```

**Ferramentas Recomendadas**:
```bash
# Formatação
pip install black
black backend/

# Linting
pip install flake8
flake8 backend/

# Type checking
pip install mypy
mypy backend/
```

##### JavaScript (Frontend)

**Estilo**: Seguimos [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

```javascript
// Bom ✅
async function fetchMovies(genre, limit = 20) {
  try {
    const response = await fetch(`${API_URL}/movies/by-genre/${genre}?limit=${limit}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching movies:', error);
    throw error;
  }
}

// Ruim ❌
function getMovies(g) {
  // Sem async/await, sem error handling
  return fetch(url).then(r => r.json());
}
```

##### CSS

**Convenções**:
- Use classes semânticas
- Organize por componentes
- Use variáveis CSS para cores e espaçamentos

```css
/* Bom ✅ */
.movie-card {
  background: var(--secondary-bg);
  border-radius: var(--border-radius);
  transition: transform 0.3s ease;
}

.movie-card:hover {
  transform: scale(1.05);
}

/* Ruim ❌ */
.mc {
  background: #1a1a1a;
  border-radius: 8px;
}
```

#### Commits

**Formato**: Seguimos [Conventional Commits](https://www.conventionalcommits.org/)

```bash
# Tipos
feat:     Nova feature
fix:      Correção de bug
docs:     Mudanças na documentação
style:    Formatação, sem mudança de código
refactor: Refatoração de código
test:     Adição de testes
chore:    Manutenção

# Exemplos
git commit -m "feat: add genre filter to search"
git commit -m "fix: resolve CORS issue in API"
git commit -m "docs: update installation guide"
git commit -m "refactor: optimize TF-IDF calculation"
```

#### Pull Requests

1. **Atualize** sua branch com a main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push** suas mudanças:
   ```bash
   git push origin feature/minha-feature
   ```

3. **Abra um Pull Request** com:
   - Título descritivo
   - Descrição das mudanças
   - Issues relacionadas
   - Screenshots (se UI)
   - Checklist de verificação

**Template de PR**:

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2
3. Verificar resultado

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Comentários adicionados em código complexo
- [ ] Documentação atualizada
- [ ] Sem warnings de lint
- [ ] Testado localmente

## Screenshots (se aplicável)
```

### Contribuindo com Documentação 📚

A documentação é tão importante quanto o código!

#### Tipos de Documentação

1. **README.md**: Visão geral do projeto
2. **MkDocs** (`docs/`): Documentação detalhada
3. **Docstrings**: Documentação inline no código
4. **Comentários**: Explicações de lógica complexa

#### Escrevendo Documentação

**Boas Práticas**:
- ✅ Seja claro e conciso
- ✅ Use exemplos práticos
- ✅ Inclua screenshots quando relevante
- ✅ Mantenha atualizado com o código
- ✅ Use português correto

**Estrutura de Documentação**:

```markdown
# Título da Página

Breve introdução.

## Seção Principal

Conteúdo detalhado.

### Subseção

Exemplos de código:

\`\`\`python
# Código aqui
\`\`\`

!!! tip "Dica"
    Informação útil.

## Próximos Passos

Links para páginas relacionadas.
```

#### Testando Documentação

```bash
# Instalar MkDocs
pip install -r requirements-docs.txt

# Servir localmente
mkdocs serve

# Build
mkdocs build
```

## Áreas que Precisam de Ajuda

### Backend
- [ ] Implementar cache de recomendações
- [ ] Adicionar testes unitários
- [ ] Otimizar algoritmo de similaridade
- [ ] Adicionar suporte a múltiplos idiomas

### Frontend
- [ ] Melhorar responsividade mobile
- [ ] Adicionar modo escuro/claro
- [ ] Implementar infinite scroll
- [ ] Adicionar animações de loading

### Dados
- [ ] Atualizar dataset regularmente
- [ ] Adicionar mais fontes de dados
- [ ] Implementar sistema de ratings de usuários

### Documentação
- [ ] Adicionar tutoriais em vídeo
- [ ] Traduzir para inglês
- [ ] Criar guia de deployment
- [ ] Adicionar FAQs

## Processo de Review

1. **Automático**: CI/CD verifica linting e testes
2. **Manual**: Maintainer revisa o código
3. **Feedback**: Discussão e ajustes
4. **Merge**: Aprovação e merge na main

## Reconhecimento

Todos os contribuidores serão:
- Listados no README
- Mencionados nas release notes
- Adicionados ao arquivo CONTRIBUTORS.md

## Dúvidas?

- 💬 [Abra uma Discussion](https://github.com/seu-usuario/sistema-de-recomendacao-de-filme/discussions)
- 📧 Entre em contato com os maintainers
- 📖 Consulte a [documentação](https://seu-usuario.github.io/sistema-de-recomendacao-de-filme/)

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a [MIT License](../LICENSE).

---

**Obrigado por contribuir!** 🙏

Cada contribuição, por menor que seja, faz diferença. Seja código, documentação, ou apenas reportar bugs - tudo ajuda a melhorar o projeto!
