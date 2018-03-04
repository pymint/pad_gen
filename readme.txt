PAD - plan de amplasament si delimitare
   Acest program genereaza pad-uri si inventare de coordonate pentru terenurile dintr-un fisier dxf ales.
1. Alege aceasta optiune daca doresti generarea unui pad cu un teren ce contine mai multe parcele si/sau constructii
   Fiecare parcela precum si constructiile trebuie sa contina in interiorul lor cate 2 texte:
    - unul ce defineste categoria de folosiinta a parcelei sau destinatia constructiei
      (categoria de folosinta pentru parcele trebuie sa fie una din 'A','CC','P','F','DR'
       destinatia constructiei trebuie sa fie una din 'CL','CAS','CIE','CA')
    - alt text ce contine numarul parcelei sau codul constructiei
      (codul constructiei trebuie sa fie de forma C1,C2,etc.)
2.3. Optiunile 2 si 3 sunt folosite pentru a genera pad pentru fiecare teren din fisierul dxf citit.
    In cazul in care toate terenurile au aceasi categorie de folosinta nu mai este necesara introducerea
textelor individuale in fisierul dxf cu categoria de folosinta a fiecarui teren. Este suficienta 
introducerea categoriei de folosinta inainte de rularea programului.
    Optiunea 2 este recomandata atunci cand doresti generarea mai multor pad-uri pentru fiecare teren in
parte cu formate de plansa si scari diferite.
    In cazul in care se stiu vecinii fiecarui teren si sunt deja introdusi intr-un proces verbal de punere
in posesie, aceste date pot fi folosite pentru crearea unui tabel in format (csv,xls sau xlsx) ce trebuie 
sa contina 5 coloane fara denumiri, in urmatoarea ordine de la stanga la dreapta:
    - numar parcela
    - vecin nord
    - vecin est
    - vecin sud
    - vecin vest
    Daca un astfel de fisier este selectat si terenurile din fisierul dxf au fiecare cate un text cu 
numarul de parcela,programul va introduce vecinii pe pad.
    In cazul in care fisierul dxf nu contine texte cu numerele de parcela pentrue fiecare contur, 
programul va folosi suprafata terenului ca si nume de parcela atat in pad cat si in titlul fisierului dxf creat.