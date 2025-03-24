mkdir stremlit-demo

## sukuria pradinius failus
```sh
uv init
```
## sukuriam ".gitignore"
## venv dažniausiai naudojamas duomenu biblioteka
```sh
uv venv
```
## turim aktivuoti venv su komanda
.venv\Scripts\activate

# Pagal modeli:
## Ollama priedas
```sh
uv add ollama
```
## tada tesem terminalo kodus
```sh
uv add openai
```

# nesu tikras kam jis reikalingas
```sh
uv add rich
```

# ChatBot
```sh
uv add streamlit
```
```sh
streamlit run main.py
```

# naudojam ši komanda kad suprastu ".evn" faila kad panaudoti tokenus
```sh
uv add python-dotenv
```


# priedas
## rei norim pašalinti openai
```sh
uv remove openai
```
## jei nera aplankalo ".venv" tada insrašom ši komanda kad inrašitu priedus
```sh
uv sync
```
## kai inrašo priedus turim ji pajungti su šio kodu
.venv\Scripts\activate



# papildomas bandymas:
uv add PyPDF2