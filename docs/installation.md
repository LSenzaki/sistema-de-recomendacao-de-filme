# Guia de Instalação

Este guia fornece instruções detalhadas para instalar e configurar o Sistema de Recomendação de Filmes.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8 ou superior** ([Download](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes Python)
- **Git** ([Download](https://git-scm.com/downloads))
- **Navegador web moderno** (Chrome, Firefox, Edge, etc.)

## Instalação Passo a Passo

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/sistema-de-recomendacao-de-filme.git
cd sistema-de-recomendacao-de-filme
```

### 2. Crie um Ambiente Virtual

!!! tip "Recomendação"
    Usar um ambiente virtual é altamente recomendado para evitar conflitos de dependências.

=== "Windows"
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

=== "Linux/Mac"
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Instale as Dependências do Backend

```bash
pip install -r backend/requirements.txt
```

Isso instalará:

- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `pandas` - Manipulação de dados
- `scikit-learn` - Machine Learning
- `nltk` - Processamento de linguagem natural
- `spacy` - NLP avançado

### 4. Baixe os Recursos do NLTK

Execute o seguinte comando para baixar os recursos necessários do NLTK:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

### 5. Prepare os Dados

Você tem duas opções:

#### Opção A: Usar Dados de Exemplo (Rápido)

```bash
python generate_data.py
```

Isso criará um arquivo `data/movies.csv` com 50 filmes de exemplo.

#### Opção B: Usar Dataset Completo do TMDB (Recomendado)

1. **Baixe os datasets do TMDB**:
   - [movies_metadata.csv](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)
   - [credits.csv](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)
   - [keywords.csv](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)

2. **Coloque os arquivos na pasta `data/extracted/`**:
   ```
   data/
   └── extracted/
       ├── movies_metadata.csv
       ├── credits.csv
       └── keywords.csv
   ```

3. **Execute o processador de dados**:
   ```bash
   python backend/data_processor.py
   ```

   Isso criará `data/processed_movies.csv` com os dados processados.

### 6. Configure Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto se precisar de configurações personalizadas:

```env
# Exemplo de configurações
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## Verificação da Instalação

### Teste o Backend

1. **Inicie o servidor**:
   ```bash
   cd backend
   python main.py
   ```

2. **Verifique se está funcionando**:
   - Abra o navegador em: `http://localhost:8000/docs`
   - Você deve ver a documentação interativa da API (Swagger UI)

3. **Teste um endpoint**:
   ```bash
   curl http://localhost:8000/movies
   ```

### Teste o Frontend

1. **Abra o frontend**:
   - Navegue até a pasta `frontend`
   - Abra `index.html` no navegador

   Ou use um servidor HTTP local:

   === "Python"
       ```bash
       cd frontend
       python -m http.server 8080
       ```
       Acesse: `http://localhost:8080`

   === "Node.js"
       ```bash
       cd frontend
       npx http-server -p 8080
       ```
       Acesse: `http://localhost:8080`

2. **Teste a funcionalidade**:
   - Digite uma busca (ex: "action movies")
   - Verifique se as recomendações aparecem

## Instalação da Documentação (Opcional)

Para visualizar esta documentação localmente:

```bash
# Instale as dependências do MkDocs
pip install -r requirements-docs.txt

# Inicie o servidor de documentação
mkdocs serve
```

Acesse: `http://127.0.0.1:8000`

## Solução de Problemas

### Erro: "Module not found"

**Problema**: Dependências não instaladas corretamente.

**Solução**:
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt --force-reinstall
```

### Erro: "NLTK resources not found"

**Problema**: Recursos do NLTK não foram baixados.

**Solução**:
```bash
python -c "import nltk; nltk.download('all')"
```

### Erro: "Port already in use"

**Problema**: A porta 8000 já está sendo usada.

**Solução**: Altere a porta no arquivo `backend/main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Mudou para 8001
```

### Erro: "Data file not found"

**Problema**: Arquivo de dados não existe.

**Solução**:
```bash
# Use dados de exemplo
python generate_data.py

# Ou processe os dados do TMDB
python backend/data_processor.py
```

### CORS Error no Frontend

**Problema**: Erro de CORS ao fazer requisições.

**Solução**: Certifique-se de que o backend está rodando e que o CORS está configurado corretamente em `backend/main.py`.

## Próximos Passos

Agora que você tem tudo instalado:

- 📖 [Aprenda a usar a API](api.md)
- 🎨 [Explore o Frontend](frontend.md)
- 📊 [Entenda o Processamento de Dados](data-processing.md)
- 🤝 [Contribua para o projeto](contributing.md)

## Atualizações

Para atualizar o projeto:

```bash
# Atualize o código
git pull origin main

# Atualize as dependências
pip install -r backend/requirements.txt --upgrade

# Reprocesse os dados se necessário
python backend/data_processor.py
```

---

!!! success "Instalação Concluída!"
    Se você chegou até aqui sem erros, parabéns! Seu sistema está pronto para uso. 🎉
