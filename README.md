# Budapesti Gazdasági Egyetem 
## Adatbányászat a Gyakorlatban
Adatalapú alkalmazások és mesterséges intelligencia

## Feldolgozott témák a kurzus alatt
1. Verziókezelés és Git
2. Bevezetés a Dash keretrendszerbe
3. Diagramok létrehozása Dash alatt
4. Pontszórási diagramok, interaktív térképek
5. Gyakorisági adatok, dinamikus komponensek, gépi tanulás
6. Felhasználói komponensek, többlapos műszerfalak, alkalmazás telepítése
7. Bevezetés a mesterséges mélytanulásba
8. Objektum detekció
9. Egyed szegmentáicó
10. Visszacsatolásos neurális hálózatok
11. Transzformáló archtiketkúrák

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
### Videó klónozásról, környezet telepítéséről és elindításáról
[Link](https://drive.google.com/file/d/1URRSjCs6gf2ArGA66jI4CfESdtuVdJx1/view?usp=drive_link)

### Javasolt fejlesztői környezetek
#### Dash alkalmazásokhoz
- Pycharm Community/Professional (Egyetemi Hallgatóknak ingyenes a Professioanal)
- Spyder (Anaconda fejlesztői csomaggal elérhető)  
A felsoroltakon kívül bármely más fejlesztői környezet is használható a kurzus alatt. 
#### Jupyter notebook fájlokhoz
- Jupyter notebook (Anaconda fejlesztői csomaggal ingyenes)
- Visual Studio Code (Jupyter bővítménnyel)
- Pycharm Professional Edition (Egyetemi Hallgatóknak ingyenes)

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
