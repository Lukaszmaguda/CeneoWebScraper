from app import app
from flask import render_template, request, redirect, url_for
from app.utils import get_element, selectors
import requests
import json
import os
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")
@app.route("/extract", methods=['POST', 'GET'])
def extract():
    if request.method == 'POST':
        product_code = request.form.get('product_code')
        url = f"https://www.ceneo.pl/{product_code}#tab=reviews"
        all_opinions = []
        while(url):
            response = requests.get(url)
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions = page_dom.select("div.js_product-review")

            for opinion in opinions:
                single_opinion = {}
                for key, value in selectors.items():
                    single_opinion[key] = get_element(opinion, *value)
                all_opinions.append(single_opinion)
            try:
                url = "https://www.ceneo.pl"+get_element(page_dom,"a.pagination__next","href")
            except TypeError:
                url=None

        if not os.path.exists(".app/data/opinions"):
            os.mkdir(".app/data/opinions")
        with open(f".app/data/opinions/{product_code}.json", "w", encoding="UTF-8") as jf:
            json.dump(all_opinions, jf, indent=4,ensure_ascii=False)
        opinions = pd.read_json(json.dumps(all_opinions,ensure_ascii=False))
        opinions.score = opinions.score.map(lambda x: float(x.split("/")[0].replace(",",".")))
        stats = {
            "opinions_count": int(opinions.opinion_id.count()),
            "pros_count": int(opinions.pros.map(bool).sum()),
            "cons_count": int(opinions.cons.map(bool).sum()),
            "avg_score": opinions.score.mean().round(2)
        }
        if not os.path.exists("./app/static/plots"):
            os.mkdir("./app/static/plots")
        stars = opinions.stars.value_counts().reindex(list(np.arange(0,5.5,0.5)), fill_value = 0)
        print(stars)
        stars.plot.bar()
        plt.title("Histogram gwiazdek")
        plt.savefig(f"./app/static/plots/{product_code}_stars.png")
        plt.close()
        recommendations = opinions.recommendation.value_counts(dropna=False)
        recommendations.plot.pie(label="", autopct="%1.1f%%")
        plt.savefig(f"./app/static/plots/{product_code}_recommendations.png")
        plt.close()
        stats['stars'] = stars.to_dict()
        stats['recommendations'] = recommendations.to_dict()
        if not os.path.exists("./app/data/stats"):
                    os.mkdir("./app/data/stats")
        with open(f"./app/data/stats/{product_code}.json", "w", encoding="UTF-8") as jf:
                    json.dump(stats, jf, indent=4, ensure_ascii=False)
        return redirect(url_for('product', code=product_code))
    return render_template("extract.html")

@app.route("/product/<code>")
def product(code):
    opinions=pd.read_json(f"./app/data/opinions/{code}.json")
    return render_template("product.html", product_code=code, opinions = opinions.to_html(header="true",table_id="opinions"))

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/author")
def author():
    return render_template("autor.html")
