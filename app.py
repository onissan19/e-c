from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/e-commerce.db'
db = SQLAlchemy(app)

@app.cli.command("initdb")
def initdb_command():
    db.create_all()
    print("base de donnee cree.")



class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80))
    description = db.relationship('Article', backref='categorie', lazy=True)
    def to_json(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description
        }

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    description = db.Column(db.String(200))
    prix = db.Column(db.Float)
    quantite = db.Column(db.Integer)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'))

    def to_json(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'prix': self.prix,
            'quantite': self.quantite
            
        }


@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        articles = Article.query.all()
        return jsonify([article.to_json() for article in articles])
    except:
        return {'error': 'erreur lors de la requete'}

@app.route('/articles/<int:id>', methods=['GET'])
def get_article(id):
    try:
        article = Article.query.get(id)
        if article is None:
            return {'error': 'erreur'}, 404
        return jsonify(article.to_json())
    except:
        return {'error': 'erreur lors de la requete'}

@app.route('/articles', methods=['POST'])
def add_article():
    try:
        article = Article(
            nom=request.json['nom'],
            description=request.json['description'],
            prix=request.json['prix'],
            quantite=request.json['quantite'],
            categorie_id=request.json['categorie_id']
        )
        categorie = Categorie.query.get(request.json['categorie_id'])
        if categorie is None:
            return "Categorie non trouver", 404
        db.session.add(article)
        db.session.commit()
        return jsonify(article.to_json()), 201
    except:
        return {'error':'erreur de requet'}, 400

@app.route('/categories', methods=['POST'])
def add_category():
    try:
        categorie = Categorie(nom=request.json['nom'])
        db.session.add(categorie)
        db.session.commit()
        return jsonify(categorie.to_json())
    except:
        return {'error': 'erreur de requet'}, 400

@app.route('/articles/<int:id>', methods=['PUT'])
def update_article(id):
    try:
        article = Article.query.get(id)
        if article is None:
            return {'error': 'not found'}, 404

        article.nom = request.json.get('nom', article.nom)
        article.description = request.json.get('description', article.description)
        article.prix = request.json.get('prix', article.prix)
        article.quantite = request.json.get('quantite', article.quantite)
    except:
        return {'error': 'erreur de requet'}, 400

    db.session.commit()
    return jsonify(article.json())

@app.route('/articles/<int:id>', methods=['DELETE'])
def delete_article(id):
    try:
        article = Article.query.get(id)
        if article is None:
            return {'error': 'not found'}, 404

        db.session.delete(article)
        db.session.commit()
        return {}, 204
    except:
        return {'error': 'erreur de requet'}, 400

@app.route('/articles/search/<keyword>', methods=['GET'])
def search_article(keyword):
    try:
        articles = Article.query.filter(Article.nom.contains(keyword)).all()
        return jsonify([article.to_json() for article in articles])
    except:
        return {'error': 'erreur de requet'}, 400


