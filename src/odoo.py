import xmlrpc.client
import re
from html import unescape

url="https://insat.odoo.com"
db="insat"
username="roua.mili@insat.ucar.tn"
password="2KXrGy22jWsYqR3"
def get_job_description(title:str):

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    print("User ID:", uid)

    if uid:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        job_title = title  # Utilisation du titre passé en paramètre

        # Recherche de l'intitulé exact ou partiel
        jobs = models.execute_kw(db, uid, password,
            'hr.job', 'search_read',
            [[['name', 'ilike', job_title]]],  # 'ilike' = insensible à la casse
            {'fields': ['name', 'description'], 'limit':1})

        if jobs:
            print("Titre :", jobs[0]['name'])
            description = (re.sub('<[^<]+?>', '', unescape(jobs[0]['description'])))
            print("Description :", description)
            return description
        else:
            print("Aucun poste trouvé avec ce nom.")
            return ""
    else:
        print("Échec de l'authentification")
        return ""
