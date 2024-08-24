# Budapesti Gazdasági Egyetem 
## Adatbányászat a Gyakorlatban
Adatbányászat és gépi tanulási algoritmusok alkalmazása

## Feldolgozott témák a kurzus alatt
1. Verziókezelés és Git
2. Bevezetés a Dash keretrendszerbe
3. Diagramok létrehozása Dash alatt
4. Pontszórási diagramok, interaktív térképek
5. Gyakorisági adatok, dinamikus komponensek, gépi tanulás
6. Felhasználói komponensek, többlapos műszerfalak, alkalmazás telepítése  
ZH
7. Bevezetés a mesterséges mélytanulásba
8. Objektum detekció
9. Egyed szegmentáicó
10. Visszacsatolásos neurális hálózatok
11. Transzformáló archtiketkúrák  
ZH

## Környezet telepítése
### Órai anyagok letöltése
1. Anaconda környezet telepítése [innen](https://www.anaconda.com/download)
2. Git telepítése [innen](https://git-scm.com/downloads)
3. Órai tárhely klónozása a számítógépre (Git bash):
```
git clone https://github.com/basictask/Adatbanyaszat.git
```
4. Új conda környezet létrehozása és aktiválása:
```
conda create -n dash python=3.11
conda activate dash
```
5. A projekt gyökérmappájában állva a következő 		paranccsal lehet minden könyvtárat telepíteni (Anaconda prompt): 
```
pip install -r requirements.txt
```

### Javasolt fejlesztői környezetek
- Pycharm Community/Professional (Egyetemi hallgatóknak ingyenes a Professioanal)
- Spyder (Anaconda fejlesztői csomaggal elérhető)  
A felsoroltakon kívül bármely más fejlesztői környezet is használható a kurzus alatt. 

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
