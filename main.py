# -*- coding: utf-8 -*-
import webapp2
import logging
import traceback
import datetime
import json
# import time

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre
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
    def put(self, mem_no):
        """ Permet d'ajouter ou modifier une personne ayant un certain NAS.

        Args:
            mem_no (str): Le NAS de la personne à ajouter (path parameter):
                       obligatoire.
        """
        try:
            # Permet de créer la clé à partir du nom du modèle
            # et de l'identifiant; il n'est pas nécessaire que cette clé
            # soit liée à un entité.
            cle = ndb.Key("Membre", mem_no)

            # Permet de récupérer l'entité (un objet "Personne") liée à la clé;
            # on obtient "None" si aucune entité n'est liée à cette clé.
            mem = cle.get()

            # Y a-t-il une entité liée à la clé ?
            if mem is None:
                # L'entité n'existe, elle sera créée (201 Created).
                status = 201
                # Création de l'entité personne avec une clé
                # (et par conséquent, un identifiant) spécifiée.
                mem = Membre(key=cle)

            else:
                # L'entité existe, elle sera mise à jour (200 OK).
                # Note : On pourrait aussi utiliser 204 sans retourner une
                # représentation de la ressource.
                status = 200

            # Le corps de la requête doit contenir une expression JSON
            # avec les données de la personne à créer ou à modifier.
            mem_json = json.loads(self.request.body)

            # Récupération et formatage du nom de la personne; seulement
            # des majuscules pour les premières lettres de chaque mot.
            mem.prenom = mem_json['prenom']
            mem.nom = mem_json['nom']
            mem.sexe = mem_json['sexe']
            mem.dateNaissance = datetime.datetime.strptime(mem_json['dateNaissance'], "%Y-%m-%d")
            mem.villeOrigine = mem_json['villeOrigine']
            mem.villeActuelle = mem_json['villeActuelle']
            mem.courriel = mem_json['courriel']
            mem.nomUtil = mem_json['nomUtil']
            mem.motPasse = mem_json['motPasse']

            # Création ou modification de l'entité "Personne".
            # Note : La propriété "dateDernModif" n'est pas spécifiée
            # car elle est automatique.
            mem.put()

            # Configuration du code de statut HTTP (201 ou 204).
            self.response.set_status(status)

            # Création d'un dictionary contenant toutes les informations
            # sur l'entité "Personne".
            mem_dict = mem.to_dict()
            # L'identifiant doit être ajouté manuellement car il ne fait pas
            # partie des propriétés de l'entité.
            mem_dict['mem_no'] = mem.key.id()
            # Création d'une expression JSON à partir du dictionary.
            # Il faut passer dans le paramètre "default" la fonction qui permet
            # de sérialiser les dates et heures.
            mem_json = json.dumps(mem_dict, default=serialiser_pour_json)

            # Configuration de l'entête HTTP "Content-Type" de la réponse.
            self.response.headers['Content-Type'] = ('application/json;' + 
                                                     ' charset=utf-8')
            # Le corps de la réponse contiendra une représentation en JSON
            # de la personne qui vient d'être créée ou modifiée.
            self.response.out.write(mem_json)

        # Exceptions en lien avec les données fournies (liées à la requête).
        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            # Bad Request.
            self.error(400)

        # Exceptions graves lors de l'exécution du code
        # (non liées à la requête).
        except Exception:
            logging.error("%s", traceback.format_exc())
            # Internal Server Error.
            self.error(500)

    def get(self, mem_no=None):
        """ Permet d'obtenir une représentation d'une personne ayant un certain
            NAS ou bien de toutes les personnes si le NAS n'est pas spécifié.

        Args:
            nas (str): Le NAS d'une certaine personne ou bien "None" pour
                       obtenir toutes les personnes  (path parameter):
                       optionnel.
        """
        try:
            if mem_no is not None:
                # Un seul membre.
                cle = ndb.Key('Membre', mem_no)
                mem = cle.get()
                # Est-ce qu'il y a un membre lié à ce numéro ?
                if (mem is None):
                    # Not Found.
                    self.error(404)
                    # Fin de l'exécution.
                    return

                mem_dict = mem.to_dict()
                mem_dict['mem_no'] = mem.key.id()
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

        webapp2.Route(r'/membres/<mem_no>',
                      handler=MembreHandler,
                      methods=['GET', 'PUT', 'DELETE']),
    ],
    debug=True)
