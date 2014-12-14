from google.appengine.ext import ndb


class Membre(ndb.Model):
    prenom = ndb.StringProperty(required=True)
    nom = ndb.StringProperty(required=True)
    sexe = ndb.StringProperty(choices=["M", "F"], required=True)
    dateNaissance = ndb.DateProperty(required=True)
    villeOrigine = ndb.StringProperty(required=True)
    villeActuelle = ndb.StringProperty(required=True)
    courriel = ndb.StringProperty(required=True)
    nomUtil = ndb.StringProperty(required=True)
    motPasse = ndb.StringProperty(required=True)


class Publication(ndb.Model):
    texte = ndb.StringProperty(required=True)
    date = ndb.DateProperty(required=True)
    noCreateur = ndb.IntegerProperty(required=True)
    noBabillard = ndb.IntegerProperty(required=True)
