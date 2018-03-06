global text_ajutor
text_ajutor = "PAD - plan de amplasament si delimitare\n\n\
   Acest program genereaza pad-uri si inventare de coordonate pentru terenurile dintr-un fisier dxf ales.\n\n\
1. Alege aceasta optiune daca doresti generarea unui pad cu un teren ce contine mai multe parcele si/sau constructii\n\
   Fiecare parcela precum si constructiile trebuie sa contina in interiorul lor cate 2 texte (sau mtext):\n\
    - unul ce defineste categoria de folosiinta a parcelei sau destinatia constructiei\n\
      (categoria de folosinta pentru parcele trebuie sa fie una din 'A','CC','P','F','DR'\n\
       destinatia constructiei trebuie sa fie una din 'CL','CAS','CIE','CA')\n\
    - alt text ce contine numarul parcelei sau codul constructiei\n\
      (codul constructiei trebuie sa fie de forma C1,C2,etc.)\n\n\
2.3. Optiunile 2 si 3 sunt folosite pentru a genera pad pentru fiecare teren din fisierul dxf citit.\n\
    In cazul in care toate terenurile au aceasi categorie de folosinta nu mai este necesara introducerea\n\
textelor individuale in fisierul dxf cu categoria de folosinta a fiecarui teren. Este suficienta introducerea categoriei\n\
de folosinta inainte de rularea programului.\n\
    Optiunea 2 este recomandata atunci cand doresti generarea mai multor pad-uri pentru fiecare teren in parte\n\
cu formate de plansa si scari diferite.\n\
    In cazul in care se stiu vecinii fiecarui teren si sunt deja introdusi intr-un proces verbal de punere in posesie,\n\
aceste date pot fi folosite pentru crearea unui tabel in format (csv,xls sau xlsx) ce trebuie sa contina 5 coloane fara\n\
denumiri, in urmatoarea ordine de la stanga la dreapta:\n\
    - numar parcela\n\
    - vecin nord\n\
    - vecin est\n\
    - vecin sud\n\
    - vecin vest\n\
    Daca un astfel de fisier este selectat si terenurile din fisierul dxf au fiecare cate un text cu numarul de parcela,\n\
programul va introduce vecinii pe pad.\n\
    In cazul in care fisierul dxf nu contine texte cu numerele de parcela pentrue fiecare contur, programul va folosi\n\
suprafata terenului ca si nume de parcela atat in pad cat si in titlul fisierului dxf creat."

from dxfgrabber import readfile as dxfread
from dxfwrite import DXFEngine as engine
from math import atan2,hypot,degrees
from numpy import abs, dot, roll
from tabulate import tabulate
import os.path
from tkinter import Tk,filedialog,messagebox,Entry,Frame,END,Button,LEFT,BOTTOM,TOP
from pandas import read_table, read_excel
from copy import deepcopy

global categorie, adresa, uat, mentiuni, executant, data, dic_poly,my_dic_poly,cc_poly,limits,centers, vecini,vecini_cond, opt, conditii, actualizare
conditii = {0:False, 1:False, 2:False}


path = os.getcwd()

vecini_cond = False
categorii = ['A','CC','P','F','DR']
coduri_cc = ['CL','CAS','CIE','CA']
#global dimensions
scales = [50,100,200,500,1000,2000,5000,10000]
papers = ['A4_P','A3_P','A3_L','A2_P','A2_L','A1_P','A1_L']
#paper formats: A4 .... A3 P ... A3 L ... A2 P ..... A2 L .... A1 P ..... A1 L
formats = [(210,297),(297,420),(420,297),(420,594),(594,420),(594, 841),(841,594)]
formats2 = [(180,277),(277,400),(390,277),(400,574),(574,400),(574,821),(821,574)]
#......... A4 P....... A3 P...... A3 L ....... A2 P ... A2 L ..... A1 P ..... A1 L 

cc_list = ['C%d'%x for x in range(1,100)] 

def get_config():
    global categorie, adresa, uat, mentiuni, executant, data
    try:
        config = read_table('%s\\config.txt'%path,header=None,delimiter='   ')
        config.set_index(0,inplace=True)
        categorie = config.loc['categorie',1]
        adresa = config.loc['adresa',1]
        uat = config.loc['uat',1]
        mentiuni = config.loc['mentiuni',1]
        executant = config.loc['executant',1]
        data = config.loc['data',1]
        messagebox.showinfo("Generare pad-uri", "Categorie de folosinta implicita: %s\nAdresa imobil: %s\nUAT: %s\nMentiuni: %s\nExecutant: %s\nData: %s"%(categorie, adresa, uat, mentiuni, executant, data))
    except: messagebox.showinfo("Generare pad-uri", "Ultima configuratie folosita nu a putut fi identificata")
           #categorie, adresa, uat, mentiuni, executant, data
    c.delete(0, END)
    c.insert(0, categorie)
    a.delete(0, END)
    a.insert(0, adresa)
    u.delete(0, END)
    u.insert(0, uat)
    m.delete(0, END)
    m.insert(0, mentiuni)
    e.delete(0, END)
    e.insert(0, executant)
    d.delete(0, END)
    d.insert(0, data)

def alege_fisier():
    global filename, conditii
    filename = filedialog.askopenfilename()
    conditii[0] = True

def alege_director():
    global folder, conditii
    folder = filedialog.askdirectory()
    conditii[1] = True

def alege_xlsx():
    global filename2, vecini_cond, vecini
    vecini_cond = True
    filename2 = filedialog.askopenfilename()
    try:
        vecini = read_excel(filename2,header=None)
    except:
        vecini = read_csv(filename2,header=None)
    try:
        vecini[0]=vecini[0].apply(lambda x:str(x))
        vecini.set_index(0,inplace=True)
    except:
        messagebox.showinfo("Generare pad-uri", "A aparut o eroare in citirea tabelului cu vecini")
        vecini_cond = False

def ajutor():
    global text_ajutor
    #text_ajutor = open("ajutor.txt",'r').read()    
    messagebox.showinfo("Generare pad-uri", text_ajutor)

def actualizeaza():
    global categorie, adresa, uat, mentiuni, executant, data, conditii
    try:
        categorie = c.get()
        adresa = a.get()
        uat = u.get()
        mentiuni = m.get()
        executant = e.get()
        data = d.get()
        messagebox.showinfo("Generare pad-uri", "Categorie de folosinta implicita: %s\nAdresa imobil: %s\nUAT: %s\nMentiuni: %s\nExecutant: %s\nData: %s"%(categorie, adresa, uat, mentiuni, executant, data))
        conditii[2] = True
    except:
        messagebox.showinfo("Generare pad-uri", "A apatur o eroare\n\nTe rog completeaza toate campurile")

def save_config():
    try:
        fisier = open('%s\\config.txt'%path,'w')
        fisier.write('categorie   %s\nadresa   %s\nuat   %s\nmentiuni   %s\nexecutant   %s\ndata   %s'%(categorie, adresa, uat, mentiuni, executant, data))
        fisier.close()
    except:
        messagebox.showinfo("Generare pad-uri", "A apatur o eroare\n\nTe rog inchide fisierul config.txt")
    
def inside(textpos,vertices):
    pvertices = deepcopy(vertices)
    pvertices.append(vertices[0])

    xmax = max([x[0] for x in vertices])
    xmin = min([x[0] for x in vertices])
    ymax = max([x[1] for x in vertices])
    ymin = min([x[1] for x in vertices])
    if textpos[0] > xmax or textpos[0]<xmin or textpos[1]<ymin or textpos[1]>ymax:
        return False
    count = 0
    X1 = textpos[0]
    X2 = xmax
    Y1 = textpos[1]
    Y2 = Y1
    #line1 = [(X1, Y1), (X2, Y2)]
    for i in range(1,len(pvertices)):
        X3 = pvertices[i-1][0]
        Y3 = pvertices[i-1][1]
        X4 = pvertices[i][0]
        Y4 = pvertices[i][1]
        #line = [(X3, Y3), (X4, Y4)]
        if (max(X1,X2) < min(X3,X4)):
            continue
        try:A1 = (Y1-Y2)/(X1-X2)
        except:continue
        try:A2 = (Y3-Y4)/(X3-X4)
        except:continue
        if A1 == A2:
            continue
        b1 = Y1-A1*X1# = Y2-A1*X2
        b2 = Y3-A2*X3# = Y4-A2*X4
        try:Xa = (b2 - b1) / (A1 - A2)
        except:continue
        if ((Xa < max( min(X1,X2), min(X3,X4))) or (Xa > min(max(X1,X2), max(X3,X4)))):
            continue
        else:
            count+=1
    if count % 2 == 0:
        return False
    else:
        return True

def north_block(f_multip):
    multip2=f_multip*0.7
    northing = engine.block(name="northing")
    northing.add(engine.circle(radius=0.5*multip2,center=(0,0)))
    northing.add(engine.line(start=(0.5*multip2,0),end=(2*multip2,0)))
    northing.add(engine.line(start=(-2*multip2,0),end=(-0.5*multip2,0)))
    northing.add(engine.line(start=(0,0.5*multip2),end=(0,23.9724*multip2)))
    northing.add(engine.solid(points=[(0,39.6746*multip2),(3.8329*multip2,16.9*multip2),(0,23.9724*multip2),(-3.8329*multip2,16.9*multip2)]))
    northing.add(engine.solid(points=[(2.6361*multip2,15.7465*multip2),(1.1442*multip2,15.7465*multip2),(1.1442*multip2,7.3423*multip2),(2.6361*multip2,7.3423*multip2)]))
    northing.add(engine.solid(points=[(1.1442*multip2,11.1275*multip2),(-0.7109*multip2,15.7465*multip2),(-0.7109*multip2,11.9614*multip2),(1.1442*multip2,7.3423*multip2)]))
    northing.add(engine.solid(points=[(-0.7109*multip2,15.7465*multip2),(-2.2028*multip2,15.7465*multip2),(-2.2028*multip2,7.3423*multip2),(-0.7109*multip2,7.3423*multip2)]))
    return(northing)

def adauga_vecini(my_dwg,f_parcela,f_pl_center,f_myx,f_myy,f_multip):
    global vecini
    vrow = vecini.loc[vecini.index == f_parcela]
    if not vrow.empty:
        my_dwg.add(engine.text(vrow.loc[f_parcela,1],insert=(f_pl_center[0],max(f_myy)), height=3*f_multip))
        my_dwg.add(engine.text(vrow.loc[f_parcela,2],insert=(max(f_myx),f_pl_center[1]), height=3*f_multip))
        my_dwg.add(engine.text(vrow.loc[f_parcela,3],insert=(f_pl_center[0],min(f_myy)), height=3*f_multip))
        my_dwg.add(engine.text(vrow.loc[f_parcela,4],insert=(min(f_myx),f_pl_center[1]), height=3*f_multip))
    else:
        messagebox.showinfo("Generare pad-uri",'Nu au fost gasiti vecini pentru parcela %s'%f_parcela)

def caroiaj(f_dwg,f_multip,f_pl_center,f_index):
    step = int(100*f_multip)
    caro_area = limits[f_index]
    caro_xmin = f_pl_center[0]-caro_area[0]/2*f_multip
    caro_xmax = f_pl_center[0]+caro_area[0]/2*f_multip
    caro_ymin = f_pl_center[1]-caro_area[1]/2*f_multip
    caro_ymax = f_pl_center[1]+caro_area[1]/2*f_multip
    caro_poly=engine.polyline(points=[(caro_xmin,caro_ymin),(caro_xmin,caro_ymax),(caro_xmax,caro_ymax),(caro_xmax,caro_ymin)])
    caro_poly.close(status=True)
    f_dwg.add(caro_poly)
    if caro_xmin%step == 0:
        xstart = caro_xmin
    else:
        xstart = (int(caro_xmin/step)+1)*step
    if caro_xmax%step == 0:
        xend = caro_xmax
    else:
        xend = int(caro_xmax/step)*step

    if caro_ymin%step == 0:
        ystart = caro_ymin
    else:
        ystart = (int(caro_ymin/step)+1)*step
    if caro_ymax%step == 0:
        yend = caro_ymax
    else:
        yend = int(caro_ymax/step)*step
    cords = []

    for y in range(ystart,yend+1,step):
        f_dwg.add(engine.line(start=(caro_xmin,y), end=(caro_xmin+9*f_multip,y)))
        f_dwg.add(engine.line(start=(caro_xmax,y), end=(caro_xmax-9*f_multip,y)))
        #dwg.add(engine.polyline(points=[(caro_xmax,y), (caro_xmax-9*f_multip,y)]))
        f_dwg.add(engine.mtext(str(y),halign=1,valign=4,insert=(caro_xmin+4.5*f_multip,y),height=1.8*f_multip))
        f_dwg.add(engine.mtext(str(y),halign=1,valign=4,insert=(caro_xmax-4.5*f_multip,y),height=1.8*f_multip))
    for x in range(xstart,xend+1,step):
        f_dwg.add(engine.line(start=(x,caro_ymin), end=(x,caro_ymin+9*f_multip)))
        f_dwg.add(engine.line(start=(x,caro_ymax), end=(x,caro_ymax-9*f_multip)))
        #dwg.add(engine.polyline(points=[(caro_xmax,y), (caro_xmax-9*f_multip,y)]))
        f_dwg.add(engine.mtext(str(x),halign=1,valign=4,insert=(x,caro_ymin+4.5*f_multip),height=1.8*f_multip,rotation=90))
        f_dwg.add(engine.mtext(str(x),halign=1,valign=4,insert=(x,caro_ymax-4.5*f_multip),height=1.8*f_multip,rotation=90))
        for y in range(ystart,yend+1,step):
            f_dwg.add(engine.line(start=(x-3*f_multip,y),end=(x+3*f_multip,y)))
            f_dwg.add(engine.line(start=(x,y-3*f_multip),end=(x,y+3*f_multip)))
    
    #northing
    n_base = (caro_xmax-19*f_multip,caro_ymax-36*f_multip)
    my_northing = north_block(f_multip)
    f_dwg.blocks.add(my_northing)
    f_dwg.add(engine.insert(blockname="northing",insert=n_base))
            
def add_tables(f_dwg,f_multip,title_base,d_corner,f_scale,f_pl_area,f_np,f_cc_n):
    f_dwg.add(engine.text('Anexa 1.35',insert = (title_base[0]+158*f_multip,title_base[1]+43.75*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.mtext('Plan de amplasament si delimitare a imobilului',halign=1,valign=4,insert = (title_base[0]+180/2*f_multip,title_base[1]+32*f_multip), height=5 * f_multip ))
    f_dwg.add(engine.text('Scara 1:%s' % f_scale,insert = (title_base[0]+79.61*f_multip,title_base[1]+27.75*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.text('Nr. cadastral',insert = (title_base[0]+2*f_multip,title_base[1]+21.25*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.text('Suprafata masurata a imobilului (mp)',insert = (title_base[0]+36.3*f_multip,title_base[1]+21.25*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.text('Adresa imobilului',insert = (title_base[0]+97*f_multip,title_base[1]+21.25*f_multip), height=2.5 * f_multip ))

    f_dwg.add(engine.text('%s' % str(f_pl_area),insert = (title_base[0]+36.3*f_multip,title_base[1]+16.25*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.text('%s' % adresa,insert = (title_base[0]+97*f_multip,title_base[1]+16.25*f_multip), height=2.5 * f_multip ))

    f_dwg.add(engine.text('Nr. carte funciara',insert = (title_base[0]+2*f_multip,title_base[1]+6.25*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.text('UNITATE ADMINISTRATIV TERITORIALA (UAT)',insert = (title_base[0]+77*f_multip,title_base[1]+6.25*f_multip), height=2.5 * f_multip ))
    f_dwg.add(engine.text('%s' %uat,insert = (title_base[0]+77*f_multip,title_base[1]+1.25*f_multip), height=2.5 * f_multip ))

    f_dwg.add(engine.polyline(points = [title_base,(title_base[0],title_base[1]+55*f_multip),(title_base[0]+180*f_multip,title_base[1]+55*f_multip)]))
    for o in range(0,26,5):
        f_dwg.add(engine.polyline(points = [(title_base[0],title_base[1]+o*f_multip),(title_base[0]+180*f_multip,title_base[1]+o*f_multip)]))
    f_dwg.add(engine.polyline(points = [(title_base[0]+75*f_multip,title_base[1]),(title_base[0]+75*f_multip,title_base[1]+10*f_multip)]))
    f_dwg.add(engine.polyline(points = [(title_base[0]+35*f_multip,title_base[1]+15*f_multip),(title_base[0]+35*f_multip,title_base[1]+25*f_multip)]))
    f_dwg.add(engine.polyline(points = [(title_base[0]+95*f_multip,title_base[1]+15*f_multip),(title_base[0]+95*f_multip,title_base[1]+25*f_multip)]))
        
    for c in [0,5,15,25+(f_np-1)*5]:
        f_dwg.add(engine.polyline(points=[(d_corner[0],d_corner[1]-c*f_multip),(d_corner[0]+180*f_multip,d_corner[1]-c*f_multip)]))

    for c in range(0,f_np*5,5):
        f_dwg.add(engine.polyline(points=[(d_corner[0],d_corner[1]-(20+c)*f_multip),(d_corner[0]+65*f_multip,d_corner[1]-(20+c)*f_multip)]))
    f_np-=1
    f_dwg.add(engine.polyline(points=[(d_corner[0]+13*f_multip,d_corner[1]-5*f_multip),(d_corner[0]+13*f_multip,d_corner[1]-(20+f_np*5)*f_multip)]))
    f_dwg.add(engine.polyline(points=[(d_corner[0]+34.5*f_multip,d_corner[1]-5*f_multip),(d_corner[0]+34.5*f_multip,d_corner[1]-(25+f_np*5)*f_multip)]))
    f_dwg.add(engine.polyline(points=[(d_corner[0]+65*f_multip,d_corner[1]-5*f_multip),(d_corner[0]+65*f_multip,d_corner[1]-(25+f_np*5)*f_multip)]))
    #f_dwg.add(engine.polyline(points=[(d_corner[0]+90*f_multip,d_corner[1]-35*f_multip),(d_corner[0]+90*f_multip,d_corner[1]-93*f_multip)]))
    f_dwg.add(engine.polyline(points=[d_corner,(d_corner[0],d_corner[1]-(25+f_np*5)*f_multip)]))

    f_dwg.add(engine.text('A. Date referitoare la teren',insert=(d_corner[0]+69.42*f_multip,d_corner[1]-3.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Nr.',insert=(d_corner[0]+4.17*f_multip,d_corner[1]-8.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('parcela',insert=(d_corner[0]+0.77*f_multip,d_corner[1]-13.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Categorie de',insert=(d_corner[0]+13.75*f_multip,d_corner[1]-8.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('folosinta',insert=(d_corner[0]+17.25*f_multip,d_corner[1]-13.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Suprafata (mp)',insert=(d_corner[0]+38.1*f_multip,d_corner[1]-11.25*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Mentiuni',insert=(d_corner[0]+115.89*f_multip,d_corner[1]-11.25*f_multip),height=2.5*f_multip))
    
    nparc = 0
    for parc in dic_poly:
        categorie_l = dic_poly[parc]['categorie']
        pl_area_l = dic_poly[parc]['pl_area']
        f_dwg.add(engine.text('%d'%(nparc+1),insert=(d_corner[0]+5.52*f_multip,d_corner[1]-(18.25+nparc*5)*f_multip),height=2.5*f_multip))
        f_dwg.add(engine.text('%s' %categorie_l,insert=(d_corner[0]+22.58*f_multip,d_corner[1]-(18.25+nparc*5)*f_multip),height=2.5*f_multip))
        f_dwg.add(engine.text('%d'%pl_area_l,insert=(d_corner[0]+(34.5+(30.5-len(str(pl_area_l))*1.84)/2)*f_multip,d_corner[1]-(18.25+nparc*5)*f_multip),height=2.5*f_multip))
        nparc+=1
        
    f_dwg.add(engine.text('%s'%mentiuni,insert=(d_corner[0]+(65+(115-len(mentiuni)*1.84)/2)*f_multip,d_corner[1]-21.25*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('%d'%f_pl_area,insert=(d_corner[0]+(34.5+(30.5-len(str(f_pl_area))*1.84)/2)*f_multip,d_corner[1]-(23.25+f_np*5)*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Total',insert=(d_corner[0]+13.36*f_multip,d_corner[1]-(23.25+f_np*5)*f_multip),height=2.5*f_multip))
    
    d_corner=(d_corner[0],d_corner[1]-(25+f_np*5)*f_multip)
    
    if f_cc_n <2: f_cc_n = 0
    else: f_cc_n-=1
    for c in [0,5,15,20,35+f_cc_n*5]+list(range(25,30+f_cc_n*5,5)):
        f_dwg.add(engine.polyline(points=[(d_corner[0],d_corner[1]-c*f_multip),(d_corner[0]+180*f_multip,d_corner[1]-c*f_multip)]))
    
    f_dwg.add(engine.polyline(points=[(d_corner[0]+13*f_multip,d_corner[1]-5*f_multip),(d_corner[0]+13*f_multip,d_corner[1]-(20+f_cc_n*5)*f_multip)]))
    f_dwg.add(engine.polyline(points=[(d_corner[0]+34.5*f_multip,d_corner[1]-5*f_multip),(d_corner[0]+34.5*f_multip,d_corner[1]-(25+f_cc_n*5)*f_multip)]))
    f_dwg.add(engine.polyline(points=[(d_corner[0]+65*f_multip,d_corner[1]-5*f_multip),(d_corner[0]+65*f_multip,d_corner[1]-(25+f_cc_n*5)*f_multip)]))
    f_dwg.add(engine.polyline(points=[(d_corner[0]+90*f_multip,d_corner[1]-(35+f_cc_n*5)*f_multip),(d_corner[0]+90*f_multip,d_corner[1]-(93+f_cc_n*5)*f_multip)]))
    f_dwg.add(engine.polyline(points=[d_corner,(d_corner[0],d_corner[1]-93*f_multip)]))

    f_dwg.add(engine.text('B. Date referitoare la constructii',insert=(d_corner[0]+69.42*f_multip,d_corner[1]-3.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Cod',insert=(d_corner[0]+4.17*f_multip,d_corner[1]-11.25*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Destinatia',insert=(d_corner[0]+13.75*f_multip,d_corner[1]-11.25*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Supraf. construita',insert=(d_corner[0]+36*f_multip,d_corner[1]-8.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('la sol (mp)',insert=(d_corner[0]+41*f_multip,d_corner[1]-13.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Mentiuni',insert=(d_corner[0]+115.89*f_multip,d_corner[1]-11.25*f_multip),height=2.5*f_multip))
    
    n_cc=0
    cc_area_tot = 0
    for cc in cc_poly:
        cod_cc = cc_poly[cc]['parcela']
        destinatie = cc_poly[cc]['categorie']
        pl_area_l = cc_poly[cc]['pl_area']
        cc_area_tot+=pl_area_l
        f_dwg.add(engine.text('%s'%cod_cc,insert=(d_corner[0]+5.52*f_multip,d_corner[1]-(18.25+n_cc*5)*f_multip),height=2.5*f_multip))
        f_dwg.add(engine.text('%s'%destinatie,insert=(d_corner[0]+22.58*f_multip,d_corner[1]-(18.25+n_cc*5)*f_multip),height=2.5*f_multip))
        f_dwg.add(engine.text('%s'%pl_area_l,insert=(d_corner[0]+(34.5+(30.5-len(str(pl_area_l))*1.84)/2)*f_multip,d_corner[1]-(18.25+n_cc*5)*f_multip),height=2.5*f_multip))
        n_cc+=1
    if len(cc_poly.keys())==0:
        f_dwg.add(engine.text('-',insert=(d_corner[0]+5.52*f_multip,d_corner[1]-18.25*f_multip),height=2.5*f_multip))
        f_dwg.add(engine.text('-',insert=(d_corner[0]+22.58*f_multip,d_corner[1]-18.25*f_multip),height=2.5*f_multip))
        f_dwg.add(engine.text('-',insert=(d_corner[0]+(34.5+(30.5-len(str(f_pl_area))*1.84)/2)*f_multip,d_corner[1]-18.25*f_multip),height=2.5*f_multip))
    
    d_corner=(d_corner[0],d_corner[1]-(f_cc_n*5)*f_multip)
    f_dwg.add(engine.text(cc_area_tot,insert=(d_corner[0]+(34.5+(30.5-len(str(cc_area_tot))*1.84)/2)*f_multip,d_corner[1]-23.25*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Total',insert=(d_corner[0]+13.36*f_multip,d_corner[1]-23.25*f_multip),height=2.5*f_multip))

    f_dwg.add(engine.text('Suprafata totala masurata a imobilului = %d mp'%f_pl_area,
            insert=(d_corner[0]+(180-(68+len(str(f_pl_area))*1.84))/2*f_multip,d_corner[1]-28.75*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Suprafata din act = %d mp'%f_pl_area,
            insert=(d_corner[0]+(180-(36+len(str(f_pl_area))*1.84))/2*f_multip,d_corner[1]-33.25*f_multip),height=2.5*f_multip))
            
    f_dwg.add(engine.text('Executant: %s'% executant, insert=(d_corner[0]+(90-(17.2+len(executant)*1.84))/2*f_multip,d_corner[1]-42.5*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Confirm executarea masuratorilor la teren,', insert=(d_corner[0]+12.3*f_multip,d_corner[1]-52*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('corectitudinea intocmirii documentatiei cadastrale', insert=(d_corner[0]+6.75*f_multip,d_corner[1]-56.23*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('si corespondenta acesteia cu realitatea din teren', insert=(d_corner[0]+6.75*f_multip,d_corner[1]-59.9*f_multip),height=2.5*f_multip))

    f_dwg.add(engine.text('Semnatura si stampila', insert=(d_corner[0]+27.72*f_multip,d_corner[1]-71.92*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Data: %s'%data, insert=(d_corner[0]+31.6*f_multip,d_corner[1]-82.23*f_multip),height=2.5*f_multip))

    f_dwg.add(engine.text('Inspector', insert=(d_corner[0]+127.8*f_multip,d_corner[1]-42.5*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Confirm introducerea imobilului in baza de date integrata', insert=(d_corner[0]+91.22*f_multip,d_corner[1]-52*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('si atribuirea numarului cadastral', insert=(d_corner[0]+110.25*f_multip,d_corner[1]-56.23*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Semnatura si parafa', insert=(d_corner[0]+119.27*f_multip,d_corner[1]-66.92*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Data ...........', insert=(d_corner[0]+125*f_multip,d_corner[1]-77.22*f_multip),height=2.5*f_multip))
    f_dwg.add(engine.text('Stampila BCPI', insert=(d_corner[0]+95.14*f_multip,d_corner[1]-82.23*f_multip),height=2.5*f_multip))

def salveaza_inventar(f_p):
    global my_dic_poly,cc_poly
    f_pl=f_p.points
    f_pl=list(dict.fromkeys(f_pl))
    f_parcela = my_dic_poly[f_p]['parcela']
    table =[]
    f_n = 0
    for i in range(len(f_pl)):
        f_n+=1
        table.append([f_n,f_pl[i][1],f_pl[i][0]])
    file = '%s_Inventar.doc'%f_parcela.replace("/","_")
    if '%s_Inventar.doc'%f_parcela.replace("/","_") in os.listdir():
        nf = 2
        while True:
            if '%s_Inventar_%d.doc'%(f_parcela.replace("/","_"),nf) not in os.listdir():
                file = '%s_Inventar_%d.doc'%(f_parcela.replace("/","_"),nf)
                break
            else:
                nf+=1
    f = open(file,'w')
    f.write('Inventar de coordonate\n')
    f.write(tabulate(table,headers=['Nr.','X','Y'],tablefmt='grid',floatfmt='.3f'))
    f.write('\nS=%d mp'%my_dic_poly[f_p]['pl_area'])
    for cc in cc_poly:
        cc_pl = cc.points
        cc_pl = list(dict.fromkeys(cc_pl))
        table = []
        for i in range(len(cc_pl)):
            f_n+=1
            table.append([f_n,cc_pl[i][0],cc_pl[i][1]])
        f.write('\n\n%s\n'%cc_poly[cc]['parcela'])
        f.write(tabulate(table,headers=['Nr.','X','Y'],tablefmt='grid',floatfmt='.3f'))
        f.write('\nS=%d mp'%cc_poly[cc]['pl_area'])
    f.close()

def cotare(f_dwg,f_p,f_multip):
    f_pl = f_p.points
    f_pl = list(dict.fromkeys(f_pl))
    f_n = 0
    for i in range(0,len(f_pl)):
        f_n+=1
        if i != len(f_pl)-1:
            radians = atan2(f_pl[i+1][1]-f_pl[i][1],f_pl[i+1][0]-f_pl[i][0])
            dist = round(hypot(f_pl[i+1][0] - f_pl[i][0], f_pl[i+1][1] - f_pl[i][1]),1)
            middle = ((f_pl[i][0]+f_pl[i+1][0])/2, (f_pl[i][1]+f_pl[i+1][1])/2)
        else:
            radians = atan2(f_pl[0][1]-f_pl[i][1],f_pl[0][0]-f_pl[i][0])
            dist = round(hypot(f_pl[0][0] - f_pl[i][0], f_pl[0][1] - f_pl[i][1]),1)
            middle = ((f_pl[i][0]+f_pl[0][0])/2, (f_pl[i][1]+f_pl[0][1])/2)
        angle = int(round(degrees(radians),0)) 
        if 90<angle<=180:
            angle = 360-(180-angle)
        elif -180<=angle<=-90:
            angle = 180-abs(angle)
        #elif -90<angle<0:
            #angle = 180 + abs(angle)
        dist_text = engine.mtext(str(dist),halign=1,valign=4,insert=middle, height=1.3*f_multip, rotation=angle)
        dist_text['layer']='Cotare'
        dist_text['color'] = 1
        f_dwg.add(dist_text)
        
        vertex=engine.text(str(i+1), insert=f_pl[i], height=1.5*f_multip)
        vertex['layer']='Cotare'
        f_dwg.add(vertex)
    for cc in cc_poly:
        cc_pl = cc.points
        cc_pl = list(dict.fromkeys(cc_pl))
        for i in range(0,len(cc_pl)):
            f_n+=1
            vertex=engine.text(str(f_n), insert=cc_pl[i], height=1.5*f_multip)
            vertex['layer']='Cotare'
            f_dwg.add(vertex)

def adauga_format_pagina(f_dwg,f_center,f_multip,f_page_f,f_index):
    if f_index in [0,2]:
        center2 = (f_center[0]-f_multip*5,f_center[1])
        temp_points = [(center2[0]-f_page_f[0]/2,center2[1]-f_page_f[1]/2),(center2[0]-f_page_f[0]/2,center2[1]+f_page_f[1]/2),
                        (center2[0]+f_page_f[0]/2,center2[1]+f_page_f[1]/2),(center2[0]+f_page_f[0]/2,center2[1]-f_page_f[1]/2)]
    else:
        temp_points = [(f_center[0]-f_page_f[0]/2,f_center[1]-f_page_f[1]/2),(f_center[0]-f_page_f[0]/2,f_center[1]+f_page_f[1]/2),
                        (f_center[0]+f_page_f[0]/2,f_center[1]+f_page_f[1]/2),(f_center[0]+f_page_f[0]/2,f_center[1]-f_page_f[1]/2)]
        temp_points3 = [(f_center[0]-f_page_f[0]/2+f_multip*20,f_center[1]-f_page_f[1]/2),
                        (f_center[0]-f_page_f[0]/2+f_multip*20,f_center[1]-f_page_f[1]/2+f_multip*297),
                        (f_center[0]-f_page_f[0]/2,f_center[1]-f_page_f[1]/2+f_multip*297)]
        f_dwg.add(engine.polyline(points = temp_points3))
    page_f2 = (formats2[f_index][0]*f_multip,formats2[f_index][1]*f_multip)
    temp_points2 = [(f_center[0]-page_f2[0]/2,f_center[1]-page_f2[1]/2),(f_center[0]-page_f2[0]/2,f_center[1]+page_f2[1]/2),
                    (f_center[0]+page_f2[0]/2,f_center[1]+page_f2[1]/2),(f_center[0]+page_f2[0]/2,f_center[1]-page_f2[1]/2)]
    poly=engine.polyline(points=temp_points)
    poly.close(status=True)
    f_dwg.add(poly)
    poly2=engine.polyline(points=temp_points2)
    poly2.close(status=True)
    f_dwg.add(poly2)

def adauga_contur_si_text(f_dwg,f_multip,f_p,numar,main_cont_bol,cc_bol,f_dic_poly):
    global opt
    f_pl=f_p.points
    f_pl=list(dict.fromkeys(f_pl))
    f_parcela = f_dic_poly[f_p]['parcela']
    f_pl_center = f_dic_poly[f_p]['pl_center']
    try: f_categorie = f_dic_poly[f_p]['categorie']
    except: f_categorie = categorie
    try: text_pos = f_dic_poly[f_p]['text_pos']
    except: text_pos = (f_pl_center[0],f_pl_center[1]-2*f_multip)
    #try: cat_pos = f_dic_poly[f_p]['cat_pos']
    cat_pos = (text_pos[0],text_pos[1]+2.1*f_multip)
    main_cont=engine.polyline(points=f_pl,flags=1)
    main_cont.close(status=True)
    f_dwg.add(main_cont)     
    if main_cont_bol:
        for vertex in f_pl:
            point = engine.point((1.0,1.0))
            point['point'] = vertex
            f_dwg.add(point)
        if opt !=3:
            f_dwg.add(engine.text(f_parcela,insert=text_pos, height=2*f_multip))
            f_dwg.add(engine.text('%s %s'%(numar,f_categorie),insert=cat_pos, height=2*f_multip))
    else:
        if not cc_bol:
            f_dwg.add(engine.text('%s %s'%(numar,f_categorie),insert=cat_pos, height=2*f_multip))
        f_dwg.add(engine.text(f_parcela,insert=text_pos, height=2*f_multip))
        
        
            
def generare():
    global dic_poly,my_dic_poly,cc_poly,limits,centers,categorie,opt, conditii
    if not conditii[2]:
        actualizeaza()
    limits = [(180,104), (267,227), (210,277), (390,401), (384,400), (564,648), (631,573)]
    centers = [(0,-31.5),(-5,-86.5),(90,0),(-5,-86.5),(85,0),(-5,-86.5),(85,0)]
    dxf = dxfread(filename)
    os.chdir(folder)

    texts = [(e.text,e.insert) for e in dxf.entities if e.dxftype=="TEXT"] + [(e.raw_text,e.insert) for e in dxf.entities if e.dxftype=="MTEXT"]
    polylines = [e for e in dxf.entities if e.dxftype in ["LWPOLYLINE","POLYLINE"]]
    dic_poly = {}
    my_dic_poly = {}
    cc_poly = {}
    my_cc_poly = []
    for p in polylines:
        pl=p.points
        pl=list(dict.fromkeys(pl))
        dic_poly[p]={}
    
        myx = [c[0] for c in pl]
        myy = [c[1] for c in pl]
        my_area = (max(myx)-min(myx),max(myy)-min(myy))
        pl_area =  int(round(0.5*abs(dot(myx,roll(myy,1))-dot(myy,roll(myx,1))),0))
        parcela = str(round(pl_area))+"mp"
        pl_center = ((max(myx)+min(myx))/2,(max(myy)+min(myy))/2)
        
        dic_poly[p]['myx'] = myx
        dic_poly[p]['myy'] = myy
        dic_poly[p]['my_area'] = my_area
        dic_poly[p]['pl_area'] = pl_area
        dic_poly[p]['parcela'] = parcela
        dic_poly[p]['pl_center'] = pl_center
        dic_poly[p]['categorie'] = categorie
        
        temp_texts = []
        cc_count = 0
        t_count = 0
        temp_dic = {}
        for t in texts:
            if inside(t[1],pl):
                if t[0] in categorii:
                    dic_poly[p]['categorie'] = t[0]
                    dic_poly[p]['cat_pos'] = t[1]
                    t_count+=1
                elif t[0] in cc_list:
                    temp_dic['parcela'] = t[0]
                    temp_dic['text_pos'] = t[1]
                    cc_count+= 1
                elif t[0] in coduri_cc:
                    temp_dic['categorie'] = t[0]
                    temp_dic['cat_pos'] = t[1]
                    cc_count+= 1
                else:
                    temp_texts.append((t[0],t[1]))
                    t_count+= 1
 
        if cc_count==2 and t_count==0: 
            my_cc_poly.append(p)
            dic_poly[p]['parcela'] = temp_dic['parcela']
            dic_poly[p]['text_pos'] = temp_dic['text_pos']
            dic_poly[p]['categorie'] = temp_dic['categorie']
            dic_poly[p]['cat_pos'] = temp_dic['cat_pos']
        if len(temp_texts)==1:
            dic_poly[p]['parcela'] = temp_texts[0][0]
            dic_poly[p]['text_pos'] = temp_texts[0][1]

    if opt == 3:
        s_total = max([dic_poly[x]['pl_area'] for x in dic_poly])
        my_poly = [x for x in dic_poly if dic_poly[x]['pl_area'] == s_total]
        my_dic_poly = {}
        my_dic_poly[my_poly[0]] = dic_poly[my_poly[0]]
        if len(polylines)>1: del dic_poly[my_poly[0]]
        for el in my_cc_poly:
            cc_poly[el] = dic_poly[el]
            del dic_poly[el]        
    else:
        my_dic_poly = dic_poly
        
    for p in my_dic_poly:

        pl=p.points
        pl=list(dict.fromkeys(pl))
        # get coordinates and middle
        myx = my_dic_poly[p]['myx']
        myy = my_dic_poly[p]['myy']
        my_area = my_dic_poly[p]['my_area']
        pl_area =  my_dic_poly[p]['pl_area']
        parcela = my_dic_poly[p]['parcela']
        pl_center = my_dic_poly[p]['pl_center']
        try: categorie = my_dic_poly[p]['categorie']
        except:eover = 0
        
        #add tables.. A4 P....... A3 P...... A3 L .... A2 P .... A2 L ..... A1 P ....... A1 L 
        titles = [(-90,83.5),(-41.5,-82),(15,83.5),(20,-169),(107,145),(107,-292.5),(230.5,232)]
        footers = [104,0,104,0,227,0,401]
        cc_n = len(cc_poly.keys())    
        #schimba dimensiuni si tabel
        if opt == 3:
            dif = (len(dic_poly.keys())+cc_n-1)*5
            limits = [(limits[0][0],limits[0][1]-dif),(limits[1][0],limits[1][1]-dif),limits[2],(limits[3][0],limits[3][1]-dif),limits[4],(limits[5][0],limits[5][1]-dif),limits[6]]
            centers = [(centers[0][0],centers[0][1]-dif/2),(centers[1][0],centers[1][1]-dif/2),centers[2],(centers[3][0],centers[3][1]-dif/2),centers[4],(centers[5][0],centers[5][1]-dif/2),centers[6]]
            titles = [titles[0],(titles[1][0],titles[1][1]+dif),titles[2],(titles[3][0],titles[3][1]+dif),titles[4],(titles[5][0],titles[5][1]+dif),titles[6]]
            footers = [footers[0]-dif,0,footers[2]-dif,0,footers[4]-dif,0,footers[6]-dif]   
            
        #get scale and page format
        all_dic = {}
        for s in scales:
            mult = s / 1000
            for i in range(len(limits)):
                if limits[i][0] * mult > my_area[0] and limits[i][1] * mult  > my_area[1]:
                    if s not in all_dic:
                        all_dic[s] = [formats[i]]
                    else:
                        all_dic[s].append(formats[i])

        allp_dic={}
        for k in all_dic:
            allp_dic[k]=[papers[formats.index(p)] for p in all_dic[k]]

        p_dic = {}
        for k in allp_dic:
            theone = max([int(x[1]) for x in allp_dic[k]])
            if "A%s_P"%theone in allp_dic[k]:
                if "A%s_L"%theone in allp_dic[k] and theone==3:
                    p_dic[k] = "A%s_L"%theone
                else:
                    p_dic[k] = "A%s_P"%theone
            else:
                p_dic[k] = "A%s_L"%theone

        if 10000 in p_dic and p_dic[10000][1] !='1':
            p_dic.pop(10000)
        for m in [5,10]:
            if m*1000 in p_dic and p_dic[m*1000][1]=='4':
                p_dic.pop(m*1000)
        for m in [50,100,200,500]:
            if m in p_dic and p_dic[m][1]!='4':
                p_dic.pop(m)
                
        temp_keys = []
        for k in p_dic:
            k_format = p_dic[k]
            for k2 in p_dic:
                if k2>k and k_format==p_dic[k2]:
                    temp_keys.append(k2)
        temp_keys = set(temp_keys)
        for key in temp_keys:
            del p_dic[key]
        
        f_min = max([x[1] for x in p_dic.items()])
        scale = [x for x in p_dic if p_dic[x]==f_min][0]
        page_format = formats[papers.index(p_dic[scale])]
        #print("\nFormat ales: 1:%s "%scale,papers[formats.index(page_format)])
        f_dic = {}
        for k in p_dic:
            f_dic[k] = formats[papers.index(p_dic[k])]

        if opt in [1,3]:
            out_dic=f_dic
        elif opt == 2:
            out_dic ={scale:page_format}
        
        once = 0    
        for k in out_dic:
            once+=1
            scale = k
            page_format = out_dic[k]
            if len(out_dic)==1:
                file = '%s_%s_1la%s_PAD.dxf'%(parcela.replace("/","_"),papers[formats.index(page_format)][:2],scale)
                if os.path.isfile(file):
                    nf = 2
                    while True:
                        if not os.path.isfile('%s_%s_1la%s_PAD_%d.dxf'%(parcela.replace("/","_"),papers[formats.index(page_format)][:2],scale,nf)):
                            file = '%s_%s_1la%s_PAD_%d.dxf'%(parcela.replace("/","_"),papers[formats.index(page_format)][:2],scale,nf)
                            break
                        else:
                            nf+=1
            else:
                file = '%s_%s_1la%s_PAD.dxf'%(parcela.replace("/","_"),papers[formats.index(page_format)],scale)
            
            dwg = engine.drawing(file)
            lco=dwg.add_layer('Cotare')
            lco['color']=7  
            
            multip = scale/1000

            index = formats.index(page_format)
            page_f = (page_format[0]*multip,page_format[1]*multip)
           
            #add contour and text
            p_n = 0
            if opt !=3:
                adauga_contur_si_text(dwg,multip,p,'1',True,False,my_dic_poly)
                dic_poly = {}
                dic_poly[p] = my_dic_poly[p]
                p_n+=1
            else:
                if len(polylines)>1: adauga_contur_si_text(dwg,multip,p,'1',True,False,my_dic_poly)
                for el in dic_poly:
                    p_n+=1
                    adauga_contur_si_text(dwg,multip,el,str(p_n),False,False,dic_poly)
                for cc in cc_poly:
                    adauga_contur_si_text(dwg,multip,cc,str(p_n),False,True,cc_poly)

            center = (pl_center[0]+centers[index][0]*multip,pl_center[1]+centers[index][1]*multip)
             
            #draw page format
            adauga_format_pagina(dwg,center,multip,page_f,index)
            
            #cotare   
            cotare(dwg,p,multip)

            #inventar
            if once ==1:
                salveaza_inventar(p)
            
            #lower left corner of title 
            my_title_base = (center[0]+titles[index][0]*multip,center[1]+titles[index][1]*multip)
            #upper left corner of footer
            my_d_corner = (my_title_base[0],my_title_base[1]-footers[index]*multip)
            add_tables(dwg,multip,my_title_base,my_d_corner,scale,pl_area,p_n,cc_n)

            #caroiaj si nord
            caroiaj(dwg,multip,pl_center,index)       

            if vecini_cond:
                try:
                    adauga_vecini(dwg,parcela,pl_center,myx,myy,multip)
                except:
                    t=0
            dwg.save()
            
    messagebox.showinfo("Generare pad-uri", "Padurie si inventarele au fost generate")

def opt1():
    global opt
    opt = 1
    if conditii[0] and conditii[1]:
        generare()
    else:
        messagebox.showinfo("Generare pad-uri","Te rog alege fisierul dxf precum si directorul in care vor fi salvate pad-urile")
def opt2():
    global opt
    opt = 2
    if conditii[0] and conditii[1]:
        generare()
    else:
        messagebox.showinfo("Generare pad-uri","Te rog alege fisierul dxf precum si directorul in care vor fi salvate pad-urile")
        
def opt3():
    global opt
    opt = 3
    if conditii[0] and conditii[1]:
        generare()
    else:
        messagebox.showinfo("Generare pad-uri","Te rog alege fisierul dxf precum si directorul in care vor fi salvate pad-urile")
        
if __name__ == "__main__":

    root = Tk()
    root.title("Generare PAD-uri 1.00")
    frame = Frame(root)
    frame.pack()
    
    bottomframe = Frame(root)
    bottomframe.pack( side = BOTTOM )

    
    b_fisier = Button(frame,
                       text="Alege fisier dxf",
                       command=alege_fisier)
    b_fisier.pack(side=LEFT)
    
    b_director = Button(frame,
                       text="Alege director",
                       command=alege_director)
    b_director.pack(side=LEFT)
    
    b_director = Button(frame,
                       text="Alege tabel cu vecini",
                       command=alege_xlsx)
    b_director.pack(side=LEFT)
    
    b_director = Button(frame,
                       text="Ajutor",
                       command=ajutor)
    b_director.pack(side=LEFT)

    b_director = Button(bottomframe,
                       text="Actualizeaza informatii",
                       fg="blue",
                       command=actualizeaza)
    b_director.pack(side=TOP)

    b_director = Button(bottomframe,
                       text="Salveaza configuratie",
                       fg="blue",
                       command=save_config)
    b_director.pack(side=TOP)
    
    b_director = Button(bottomframe,
                       text="Foloseste ultima configuratie",
                       fg="blue",
                       command=get_config)
    b_director.pack(side=TOP)
    
    b_ruleaza1 = Button(bottomframe,
                       text="3. Genereaza pad-uri cu formatul de plansa optim",
                       fg="green",
                       command=opt2)
    b_ruleaza1.pack(side=BOTTOM)
    
    b_ruleaza2 = Button(bottomframe,
                       text="2. Genereaza pad-uri cu toate formatele de plansa optime posibile",
                       fg="green",
                       command=opt1)
    b_ruleaza2.pack(side=BOTTOM)
    
    b_ruleaza2 = Button(bottomframe,
                       text="1. Genereaza pad cu un teren format din mai multe parcele\nsi/sau cu constructii",
                       fg="green",
                       command=opt3)
    b_ruleaza2.pack(side=BOTTOM)
    '''
    b_stop = Button(frame,
                       text="Inchide",
                       fg="red",
                       command=exit)
    b_stop.pack(side=BOTTOM)'''
    
    global c
    c = Entry(root)
    c.pack()
    c.focus_set()
    c.delete(0, END)
    c.insert(0, "categorie de folosinta")
    global a
    a = Entry(root)
    a.pack()
    a.focus_set()
    a.delete(0, END)
    a.insert(0, "Adresa imobil")
    global u
    u = Entry(root)
    u.pack()
    u.focus_set()
    u.delete(0, END)
    u.insert(0, "UAT")
    global m
    m = Entry(root)
    m.pack()
    m.focus_set()
    m.delete(0, END)
    m.insert(0, "Mentiuni")
    global e
    e = Entry(root)
    e.pack()
    e.focus_set()
    e.delete(0, END)
    e.insert(0, "Executant")
    global d
    d = Entry(root)
    d.pack()
    d.focus_set()
    d.delete(0, END)
    d.insert(0, "Data")
    root.mainloop()
