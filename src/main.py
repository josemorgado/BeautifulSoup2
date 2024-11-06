#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#            VENTANA PRINCIPAL
def ventana_principal():
    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Titulo", command=buscarTitulo)
    menubuscar.add_command(label="Fecha", command=buscarFecha   )
    menubuscar.add_command(label="Generos", command=buscarGenero)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()

#             FUNCIONES CARGAR
def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operacion puede ser lenta")
    if respuesta:
        almacenar_bd()

def extraerDatos(): 
    res=[]
    f=urllib.request.urlopen("https://www.elseptimoarte.net/estrenos/2024/")
    s=BeautifulSoup(f,"lxml")
    cont=s.find("section",id="collections").find("ul",class_="elements")
    lista=cont.find_all("li")
    links=[]
    i=0
    for l in lista:
        if i<5:
            links.append(l.a["href"])
            i+=1
    for link in links:
        f2=urllib.request.urlopen("https://www.elseptimoarte.net"+str(link))
        s2=BeautifulSoup(f2,"lxml")
        titulo=s2.find("dt",string="Título").find_next("dd").text.strip()
        tituloOriginal=s2.find("dt",string="Título original").find_next("dd").text.strip()
        pais=s2.find("dt",string="País").find_next("dd").text.strip()
        pais = ' '.join(pais.split())
        estrenoEspaña=s2.find("dt",string="Estreno en España").find_next("dd").text
        estrenoEspañaParseado= parsingDate(estrenoEspaña)
        director= s2.find("dt",string="Director").find_next("dd").text.strip()
        director = ' '.join(director.split())
        genero=s2.find("div",id="datos_pelicula").find("p",class_="categorias").text.strip()
        genero = ' '.join(genero.split())
        res.append((titulo,tituloOriginal,pais,estrenoEspañaParseado,director,genero))
    print("FUNCION EXTRAER DATOS FUNCIONA CORRECTAMENTE")
    return res

def almacenar_bd():
    conn=sqlite3.connect('peliculas.db')
    conn.text_factory=str
    conn.execute('DROP TABLE IF EXISTS PELICULAS')
    conn.execute('''
    CREATE TABLE PELICULAS(
    TITULO    TEXT,
    TITULO_ORIGINAL    TEXT,
    PAIS    TEXT,
    FECHA    DATE,
    DIRECTOR    TEXT,
    GENERO    TEXT
    );
    ''')
    listaDatos=extraerDatos()
    i=0
    for dato in listaDatos:
        conn.execute('INSERT INTO PELICULAS VALUES (?,?,?,?,?,?)',dato)
        print(dato)
        i+=1
    conn.commit()
    cursor=conn.execute('SELECT COUNT(*) FROM PELICULAS')
    numeroRegistros=cursor.fetchone()[0]
    messagebox.showinfo("Base de Datos creada", "La Base de Datos se ha llenado con "+str(numeroRegistros)+" registros.")
    conn.close()
#                FUNCIONES LISTAR

def listar():
    
    conn= sqlite3.connect('peliculas.db')
    conn.text_factory=str
    cursor=conn.execute('SELECT * FROM PELICULAS')
    listarTPD(cursor)
    conn.close()
      
def listarTPD(cursor):
    
#    cursor = extraerDatos()
    v = Toplevel()
    v.title("PELICULAS")
    
    # Barra de desplazamiento
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    
    # Lista donde mostrar los datos
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    
    # Procesar registros del cursor
    registros_encontrados = False  # Añadir bandera para saber si se encontraron registros
    
    for row in cursor:
        registros_encontrados = True  # Si hay registros, se pone en True
        print("Registro encontrado: ", row)  # Para verificar que sí encuentra registros
        lb.insert(END, str(row[0]).upper())  # Insertar título
        lb.insert(END, "\n")
        lb.insert(END, "PAIS: " + str(row[2]))  # Insertar país
        lb.insert(END, "\n")
        lb.insert(END, "Director/a: " + str(row[4]))  # Insertar director
        lb.insert(END, "\n\n")
    
    # Si no hay registros, mostrar mensaje en consola y en la interfaz
    if not registros_encontrados:
        print("No se encontraron registros")
        lb.insert(END, "No se encontraron registros.")
    
    # Mostrar la lista y configurar la barra de desplazamiento
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
def listarTF(cursor):
    
#    cursor = extraerDatos()
    v = Toplevel()
    v.title("PELICULAS")
    
    # Barra de desplazamiento
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    
    # Lista donde mostrar los datos
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    
    # Procesar registros del cursor
    registros_encontrados = False  # Añadir bandera para saber si se encontraron registros
    
    for row in cursor:
        registros_encontrados = True  # Si hay registros, se pone en True
        print("Registro encontrado: ", row)  # Para verificar que sí encuentra registros
        lb.insert(END, str(row[0]).upper())  # Insertar título
        lb.insert(END, "FECHA: " + str(row[3]))  # Insertar fecha
        lb.insert(END, "\n\n")
    
    # Si no hay registros, mostrar mensaje en consola y en la interfaz
    if not registros_encontrados:
        print("No se encontraron registros")
        lb.insert(END, "No se encontraron registros.")
    
    # Mostrar la lista y configurar la barra de desplazamiento
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
    
#                FUNCIONES BUSCAR
    
def buscarTitulo():
    def listar(event=None):
        conn=sqlite3.connect('peliculas.db')
        conn.text_factory=str
        cursor=conn.execute("SELECT * FROM PELICULAS WHERE TITULO LIKE '%"+str(cont.get().upper())+"%'")
        listarTPD(cursor)
        conn.close()
    
    v=Toplevel()
    v.title("BUSCAR POR TITULO")
    label= Label(v,text="Introduzca titulo:")
    label.pack(side=LEFT)
    Bu=Button(v,text="Buscar",command=listar)
    Bu.pack(side=RIGHT)
    cont= Entry(v,text="titulo")
    cont.pack(side=RIGHT)
    cont.bind("<Return>",listar)
  
def buscarFecha():
    def listar(event=None):
        conn=sqlite3.connect('peliculas.db')
        conn.text_factory=str
        contai=cont.get()
        cursor=conn.execute("SELECT * FROM PELICULAS WHERE FECHA >= '%"+str(contai)+"%'")
        listarTF(cursor)
        conn.close()
    
    v=Toplevel()
    v.title("BUSCAR POR FECHA")
    label= Label(v,text="Introduzca fecha en formato dd-mm-aaaa:")
    label.pack(side=LEFT)
    Bu=Button(v,text="Buscar",command=listar)
    Bu.pack(side=RIGHT)
    cont= Entry(v,text="fecha")
    cont.pack(side=RIGHT)
    cont.bind("<Return>",listar)
   
def buscarGenero():
    def listar(event=None):
        conn=sqlite3.connect('peliculas.db')
        conn.text_factory=str
        contai=cont.get()
        cursor=conn.execute("SELECT * FROM PELICULAS WHERE GENERO LIKE '%"+str(contai)+"%'")
        listarTF(cursor)
        conn.close()
    conn=sqlite3.connect("peliculas.db")
    conn.text_factory=str
    cursor=conn.execute("SELECT DISTINCT GENERO FROM PELICULAS")
    opciones=set()
    for row in cursor:
        generos=row[0].split(",")
        for genero in generos:
            opciones.add(genero.strip())
            
    v=Toplevel()
    
    v.title("BUSCAR POR GENERO")
    label= Label(v,text="Elija el genero:")
    label.pack(side=LEFT)
    Bu=Button(v,text="Buscar",command=listar)
    Bu.pack(side=RIGHT)
    cont= Spinbox(v,text="Genero",values=list(opciones))
    cont.pack(side=RIGHT)
    cont.bind("<Return>",listar)
    
    conn.close()
#                FUNCIONES AUXILIARES

def parsingDate(fecha):
    partes= fecha.split("/")
    res=str(partes[2])+"-"+str(partes[1])+"-"+str(partes[0])
    return res

def parsingDate2(fecha):
    partes= fecha.split("-")
    res=str(partes[2])+"-"+str(partes[1])+"-"+str(partes[0])
    return res
if __name__ == "__main__":
    ventana_principal()



















