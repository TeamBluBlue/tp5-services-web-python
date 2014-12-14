# -*- coding: utf-8 -*-
import webapp2
import logging
import traceback
import datetime
import json

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre, Publication


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
    def get(self, memNo=None):
        try:
            if memNo is not None:
                # Un seul membre.
                cle = ndb.Key('Membre', memNo)
                mem = cle.get()
                # Est-ce qu'il y a un membre lié à ce numéro ?
                if (mem is None):
                    # Not Found.
                    self.error(404)
                    # Fin de l'exécution.
                    return

                mem_dict = mem.to_dict()
                mem_dict['memNo'] = mem.key.id()
                json_data = json.dumps(mem_dict, default=serialiser_pour_json)

            else:
                # Tous les membres.
                list_mem = []
                # Création d'une requête sur le "Datastore".
                requete = Membre.query()

                # Paramètre "nom"
                nom = self.request.get('nom')
                if (nom != ''):
                    requete = requete.filter(Membre.nom == nom or
                                             Membre.prenom == nom)

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

                #  Parcours des personnes retournées par la requête.
                for mem in requete:
                    mem_dict = mem.to_dict()
                    mem_dict['memNo'] = mem.key.id()
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

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/',
                      handler=MainPageHandler,
                      methods=['GET']),
        # Cet URI utilise "PersonneHandler.get" et "PersonneHandler.delete"
        # sans le "path parameter" "nas".
        webapp2.Route(r'/membres',
                      handler=MembreHandler,
                      methods=['GET']),
    ],
    debug=True)
