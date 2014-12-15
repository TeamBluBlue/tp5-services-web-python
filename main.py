# -*- coding: utf-8 -*-
import webapp2
import logging
import traceback
import datetime
import json

from google.appengine.ext import ndb
from google.appengine.ext import db
from models import Membre, Publication, Demande, Amis


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
                requete = requete.filter(
                    ndb.OR(Membre.nom == nom, Membre.prenom == nom))

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
                mem_dict['no'] = mem.key.id()
                # Ajout de la personne dans la liste.
                list_mem.append(mem_dict)

            json_data = json.dumps(list_mem, default=serialiser_pour_json)

            self.response.set_status(200)
            self.response.headers[
                'Content-Type'] = ('application/json; charset=utf-8')
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


class AmisHandler(webapp2.RequestHandler):

    def get(self, mem_no):
        try:
            # Clé du membre.
            cle_membre = ndb.Key('Membre', int(mem_no))
            # Le propriétaire doit exister.
            if (cle_membre.get() is None):
                self.error(404)
                return

            # Tous les membres.
            list_amis = []

            # Création d'une requête sur le "Datastore".
            for amis in Amis.query().filter(Amis.no1 == int(mem_no)).fetch():
                ami = Membre.get_by_id(amis.no2)
                ami_dict = ami.to_dict()
                ami_dict['id'] = ami.key.id()
                # Ajout de la personne dans la liste.
                list_amis.append(ami_dict)

            for amis in Amis.query().filter(Amis.no2 == int(mem_no)).fetch():
                ami = Membre.get_by_id(amis.no1)
                ami_dict = ami.to_dict()
                ami_dict['id'] = ami.key.id()
                ami_dict['dateAmitie'] = amis.dateAmitie
                # Ajout de la personne dans la liste.
                list_amis.append(ami_dict)

            json_data = json.dumps(list_amis, default=serialiser_pour_json)

            self.response.set_status(200)
            self.response.headers[
                'Content-Type'] = ('application/json; charset=utf-8')
            self.response.out.write(json_data)

        except (db.BadValueError, ValueError, KeyError):
            logging.error("%s", traceback.format_exc())
            self.error(400)

        except Exception:
            logging.error("%s", traceback.format_exc())
            self.error(500)


class UtilitaireHandler(webapp2.RequestHandler):

    def delete(self):
        """ Permet de supprimer toutes les entités existantes
        """
        try:
            # Suppression de toutes les demandes d'amitié.
            ndb.delete_multi(Amis.query().fetch(keys_only=True))
            # Suppression de toutes les demandes d'amitié.
            ndb.delete_multi(Demande.query().fetch(keys_only=True))
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
            fichier_json = open("twitface.json")
            bd = json.load(fichier_json)
            fichier_json.close()

            list_mem = []
            for mem_json in bd["membres"]:
                nom_split = mem_json['MemNom'].split(" ", 1)
                cle = ndb.Key("Membre", int(mem_json["MemNo"]))
                mem = Membre(key=cle)
                mem.prenom = nom_split[0]
                mem.nom = nom_split[1]
                mem.sexe = mem_json['MemSexe']
                mem.dateNaissance = datetime.datetime.strptime(
                    mem_json['MemDateNaissance'], "%Y-%m-%d")
                mem.villeOrigine = mem_json['MemVilleOrigine']
                mem.villeActuelle = mem_json['MemVilleActuelle']
                mem.courriel = mem_json['MemCourriel']
                mem.nomUtil = mem_json['MemNomUtil']
                mem.motPasse = mem_json['MemMotPasse']

                mem.put()

                mem_dict = mem.to_dict()
                mem_dict['no'] = mem.key.id()

                list_mem.append(mem_dict)

            list_pub = []
            for pub_json in bd["publications"]:
                cle = ndb.Key("Publication", int(pub_json["PubNo"]))
                pub = Publication(key=cle)
                pub.texte = pub_json["PubTexte"]
                pub.date = datetime.datetime.strptime(
                    pub_json["PubDate"], "%Y-%m-%d")
                pub.noCreateur = int(pub_json["MemNoCreateur"])
                pub.noBabillard = int(pub_json["MemNoBabillard"])

                pub.put()

                pub_dict = pub.to_dict()
                pub_dict['pubNo'] = pub.key.id()

                list_pub.append(pub_dict)

            list_dem = []
            for dem_json in bd["demandes_amis"]:
                cle_proprio = ndb.Key("Membre", int(dem_json["MemNoInvite"]))
                dem = Demande(parent=cle_proprio)
                dem.no = int(dem_json["DemAmiNo"])
                dem.date = datetime.datetime.strptime(
                    dem_json["DemAmiDate"], "%Y-%m-%d")
                dem.noDemandeur = int(dem_json["MemNoDemandeur"])

                cle_dem = dem.put()

                dem_dict = dem.to_dict()
                dem_dict['id'] = cle_dem.id()
                dem_dict['parent-noInvite'] = cle_proprio.id()

                list_dem.append(dem_dict)

            list_amis = []
            i = 0
            for amis_json in bd["amis"]:
                cle = ndb.Key("Amis", i)
                amis = Amis(key=cle)
                amis.no1 = int(amis_json["MemNo1"])
                amis.no2 = int(amis_json["MemNo2"])
                amis.dateAmitie = datetime.datetime.strptime(
                    amis_json["DateAmitie"], "%Y-%m-%d")

                amis.put()

                amis_dict = amis.to_dict()
                amis_dict['id'] = amis.key.id()

                list_amis.append(amis_dict)
                i += 1

            self.response.set_status(201)

            # self.response.headers['Location'] = ("/membres")

            # Le corps de la réponse contiendra une représentation en JSON
            # de la bd qui vient d'être créée.
            self.response.headers[
                'Content-Type'] = ('application/json; charset=utf-8')
            self.response.out.write(
                json.dumps(
                    [list_mem, list_pub, list_dem, list_amis],
                    default=serialiser_pour_json
                )
            )

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
        webapp2.Route(r'/membres',
                      handler=MembreHandler,
                      methods=['GET']),
        webapp2.Route(r'/amis/<mem_no>',
                      handler=AmisHandler,
                      methods=['GET']),
    ],
    debug=True)
