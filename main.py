# -*- coding: utf-8 -*-
import webapp2


class MainPageHandler(webapp2.RequestHandler):

    def get(self):
        # Permet de vérifier si le service Web est en fonction.
        # On pourrait utiliser cette page pour afficher de l'information
        # (au format HTML) sur le service Web REST.
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        self.response.out.write('Démo "Service Web REST avec' +
                                'Google App Engine" en fonction !!!')

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/',
                      handler=MainPageHandler,
                      methods=['GET'])
    ],
    debug=True)
