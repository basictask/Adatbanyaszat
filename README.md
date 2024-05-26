# Budapesti Gazdasági Egyetem 
## Adatbányászat a Gyakorlatban
Adatbányászat és gépi tanulási algoritmusok alkalmazása

## Feldolgozott témák a kurzus alatt
```
COMING SOON
```

## Környezet telepítése
Anaconda Prompt segítségével a projekt gyökérmappájában állva a következő paranccsal lehet minden könyvtárat telepíteni: 
```
pip install -r requirements.txt
```

## Mappák struktúrája
A gyökérmappában található scriptek:  
- `merge_pdfs.py`: Konkatenálja az összes pdf-et egy dokumentummá a gyökérmappába.  
- `render_graph.py`: Renderel minden dot gráfot az összes mappában.  
- `render_pdf.py`: Renderel minden LaTeX fájlt pdf formátumba.  
    
Minden mappában két almappa található:  
- `code`: Esettanulány, ami megvalósítja a tanult témakört.  
- `doc`: Dokumentáció LaTeX és pdf formátumban.  
	- `images`: Diagramok és képek a dokumentációban. Itt megtalálható egy témának megfelelően elnevezeett Jupyter notebook, ami a képek generálásáért felelős. Az itt található programkód publikus és szabadon felhasználható az órai munka során.  
	- `graphs` (opcionális): Gráfok dot formátumban, amit a Graphviz szoftver segítségével lehet lerenderelni.   
