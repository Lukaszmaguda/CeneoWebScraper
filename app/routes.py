from app import app
from flask import render_template

@app.route("/")
@app.route("/strona_glowna")
def strona_glowna():
    return render_template("strona_glowna.html")

@app.route("/autor")
def autor():
    return render_template("autor.html")

@app.route("/Ekstrakcja")
def ekstrakcja():
    return render_template("ekstrakcja_opinii.html")

@app.route("/Lista_Produktow")
def lista_poduktow():
    return render_template("lista_produktow.html")

@app.route("/Strona główa")
def strona_glowna():
    return render_template("strona_glowna.html")