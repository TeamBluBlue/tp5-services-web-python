# -*- coding: utf-8 -*-
import webapp2
import logging
import traceback
import datetime
import json
# import time

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre, Publication
from datetime import date
# from time import strptime


def serialiser_pour_json(objet):
    """ Permet de sérialiser les dates et heures pour transformer
        un objet en JSON.

        Args:
            objet (obj): L'objet à sérialiser.

        Returns:
            obj : Si c'est une date et heure, retourne une version sérialisée
                  selon le format ISO (str); autrement, retourne l'objet
                  original non modifié.
        """
    if isinstance(objet, datetime.datetime):
        # Pour une date et heure, on retourne une chaîne
        # au format ISO (sans les millisecondes).
        return objet.replace(microsecond=0).isoformat()
    elif isinstance(objet, datetime.date):
        # Pour une date, on retourne une chaîne au format ISO.
        return objet.isoformat()
    else:
        # Pour les autres types, on retourne l'objet tel quel.
        return objet


class MembreHandler(webapp2.RequestHandler):

    def get(self):
        try:
            # Tous les membres.
            list_mem = []

            # Création d'une requête sur le "Datastore".
            requete = Membre.query()

            # Paramètre "nom"
            nom = self.request.get('nom')
            if (nom != ''):
                requete = requete.filter(ndb.OR(Membre.nom == nom,
                                                Membre.prenom == nom))

            # Paramètre "ville-actuelle"
            villeAct = self.request.get('ville-actuelle')
            if (villeAct != ''):
                requete = requete.filter(Membre.villeActuelle == villeAct)

            # Paramètre "ville-origine"
            villeOri = self.request.get('ville-origine')
            if (villeOri != ''):
                requete = requete.filter(Membre.villeOrigine == villeOri)

            # Paramètre "sexe"
            sexe = self.request.get('sexe')
            if (sexe == 'M' or sexe == 'F'):
                requete = requete.filter(Membre.sexe == sexe)

            requete = requete.order(Membre.nom).fetch(20)
            #  Parcours des personnes retournées par la requête.
            for mem in requete:
                mem_dict = mem.to_dict()
                mem_dict['mem_no'] = mem.key.id()
                # Ajout de la personne dans la liste.
                list_mem.append(mem_dict)

            json_data = json.dumps(list_mem, default=serialiser_pour_json)

            self.response.set_status(200)
            self.response.headers['Content-Type'] = ('application/json;' +
                                                     ' charset=utf-8')
            self.response.out.write(json_data)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)


class MainPageHandler(webapp2.RequestHandler):

    def get(self):
        # Permet de vérifier si le service Web est en fonction.
        # On pourrait utiliser cette page pour afficher de l'information
        # (au format HTML) sur le service Web REST.
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        self.response.out.write('Travail Pratique "Tp-ython-5" en fonction!')


class UtilitaireHandler(webapp2.RequestHandler):

    def delete(self):
        """ Permet de supprimer toutes les entités existantes
        """
        try:
            # Suppression de toutes les publications.
            ndb.delete_multi(Publication.query().fetch(keys_only=True))
            # Suppression de tous les membres.
            ndb.delete_multi(Membre.query().fetch(keys_only=True))

            # No Content.
            self.response.set_status(204)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)

    def post(self):

        try:
            fichierJson = open("twitface.json")
            bdd = json.load(fichierJson)
            fichierJson.close()

            for mem_json in bdd["membres"]:
                cle = ndb.Key("Membre", int(mem_json["MemNo"]))
                mem = Membre(key=cle)
                mem.prenom = mem_json['MemNom']
                mem.nom = mem_json['MemNom']
                mem.sexe = mem_json['MemSexe']
                mem.dateNaissance = datetime.datetime.strptime(mem_json['MemDateNaissance'], "%Y-%m-%d")
                mem.villeOrigine = mem_json['MemVilleOrigine']
                mem.villeActuelle = mem_json['MemVilleActuelle']
                mem.courriel = mem_json['MemCourriel']
                mem.nomUtil = mem_json['MemNomUtil']
                mem.motPasse = mem_json['MemMotPasse']

                mem.put()

            for pub_json in bdd["publications"]:
                cle = ndb.Key("Publication", int(pub_json["PubNo"]))
                pub = Publication(key=cle)
                pub.texte = pub_json["PubTexte"]
                pub.date = datetime.datetime.strptime(pub_json["PubDate"], "%Y-%m-%d")
                pub.noCreateur = pub_json["PubNoCreateur"]
                pub.noBabillard = pub_json["PubNoBabillard"]

            self.response.set_status(201)

            # Ajout de l'URI de la ressource qui vient d'être créée
            # dans l'en-tête HTTP "Location" de la réponse.
            # Note : On utilise l'identifiant généré (et non pas la clé).
            self.response.headers['Location'] = ("/membres")

            # Le corps de la réponse contiendra une représentation en JSON
            # de l'animal qui vient d'être créé.
            self.response.headers['Content-Type'] = ('application/json;' + 
                                                     ' charset=utf-8')
            self.response.out.write()

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/',
                      handler=MainPageHandler,
                      methods=['GET']),
        webapp2.Route(r'/datastore',
                      handler=UtilitaireHandler,
                      methods=['POST', 'DELETE']),
        # Cet URI utilise "PersonneHandler.get" et "PersonneHandler.delete"
        # sans le "path parameter" "nas".
        webapp2.Route(r'/membres',
                      handler=MembreHandler,
                      methods=['GET']),

        webapp2.Route(r'/membres',
                      handler=MembreHandler,
                      methods=['GET']),
    ],
    debug=True)
