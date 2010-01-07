import Foundation
# -*- coding: utf-8 -*-

languageCode=Foundation.NSUserDefaults.standardUserDefaults().objectForKey_('AppleLanguages')[0]
#languageCode='nl'

translations={
    'da': # Danish
    {'Yes' : 'Ja',
     'No' : 'Nej',

     'Recordings by Series' : 'Optagelser efter serier',
     'Favorite Channels' : 'Favoritkanaler',
     'All Channels' : 'Alle kanaler',
     'Program Guide' : 'Programguide',
     
     'Delete All' : 'Slet alle',
     'Play' : 'Play',
     'Restart' : 'Genstart',
     'Delete' : 'Slet',
     
     'Delete Recording(s)' : 'Slet optagelse(r):',
     
     'Are you sure you want to delete %d recordings from %s?' : 'Er du sikker på at du vil slette %d optagelse(r) fra %s?',
     'Are you sure you want to delete' : 'Er du sikker på at du vil slette', # Shouldn't this end in a question mark?
     
     'ComSkipper  [Off]' : 'ComSkipper  [Deaktivér]',
     'ComSkipper  [On]' : 'ComSkipper  [Aktivér]',
     #'Mark Commercials' : 'Markér reklamer',
     #"Mark Commercials [Running]" : "Markér reklamer [løbende]", # Some context of "Running" is probably needed; the translation might not be right!
     
     
     'Launching EyeTV' : 'Starter EyeTV',
     'Now Recording' : 'Optager',
     "Currently recording channel %s. Program info is not available." : "Optager fra kanal %s. Programinformation ikke tilgængelig.",
     
     'Episode' : 'Episode',
     'Channel' : 'Kanal',
     'Position' : 'Position',
     'Recorded at' : 'Optaget', #What will follow? Timestamp?
     "Next" : "Næste",
     "Time" : "Tid"
     },

    'es':  # Spanish
    {'Yes' : 'Sí',
     'No' : 'No',

     'Recordings by Series' : 'Grabaciones',
     'Favorite Channels' : 'Canales Favoritos',
     'All Channels' : 'Todos los Canales',
     'Program Guide' : 'Programación',
     
     'Delete All' : 'Eliminar Todo',
     'Play' : 'Reproducir',
     'Restart' : 'Reiniciar',
     'Delete' : 'Eliminar',
     
     'Delete Recording(s)' : 'Eliminar Grabación(es):',
     
     'Are you sure you want to delete %d recordings from %s?' : 'Seguro que quieres eliminar %d grabaciones de %s?',
     'Are you sure you want to delete' : 'Seguro que quieres eliminar?',
     
     'ComSkipper  [Off]' : 'ComSkipper  [Desactivado]',
     'ComSkipper  [On]' : 'ComSkipper  [Activado]',
     #'Mark Commercials' : 'Señalar anuncios',
     #"Mark Commercials [Running]" : "Señalar anuncios [Funcionando]",
     
     
     'Launching EyeTV' : 'Abriendo EyeTV',
     'Now Recording' : 'Grabando...',
     "Currently recording channel %s. Program info is not available." : "Grabación en curso de %s. Información del programa no disponible.",
     
     'Episode' : 'Episodio',
     'Channel' : 'Canal',
     'Position' : 'Posición',
     'Recorded at' : 'Grabado a las',
     "Next" : "Siguiente",
     "Time" : "Fecha"
     },

    'fi':  # Finnish
    {'Yes' : u'Kyllä',
     'No'  : u'Ei',
     
     'Recordings by Series' : u'Tallenteet',
     'Favorite Channels' : u'Suosikit',
     'All Channels' : u'Kanavat',
     'Program Guide' : u'Ohjelmaopas',
     
     'Delete All' : u'Poista Kaikki',
     'Play' : u'Toista',
     'Restart' : u'Toista Alusta',
     'Delete' : u'Poista',
     
     'Delete Recording(s):' : u'Poista tallenne/tallenteet',
     
     'Are you sure you want to delete %d recordings from %s?' : u'Haluatko varmasti poistaa %d tallennetta kansiosta %s',
     'Are you sure you want to delete' : u'Haluatko varmasti poistaa? ',
     
     'ComSkipper                      [Off]' : u'Mainosten ohitus 			[Pois]',
     'ComSkipper                       [On]' : u'Mainosten ohitus 		  [Päällä]',
     #'Mark Commercials' : u'Merkitse mainokset',
     #"Mark Commercials    [Running]" : u'Merkitään mainoksia, käynnissä...',


     'Launching EyeTV' : u'Käynnistetään EyeTV',
     'Now Recording' : u'Tallennus käynnissä',
     "Currently recording channel %s.  Program info is not available." : u'Kanavan %s tallennus käynnissä. Ohjelman tiedot eivät ole saatavilla.', 
     
     'Episode' : u'Jakso',
     'Channel' : u'Kanava',
     'Position' : u'Sijainti',
     'Recorded at' : u'Tallennettu',
     "Next" : u'Seuraavana',
     "At" : u'Aika'
     },
    


    'fr': # French
    {'Yes' : u'Oui',
     'No'  : u'Non',
     
     'Recordings by Series' : u'Enregistrements par Séries',
     'Favorite Channels' : u'Chaînes Préférées',
     'All Channels' : u'Toutes les Chaînes',
     'Program Guide' : u'Guide des Programmes',
     
     'Delete All' : u'Tout Effacer',
     'Play' : u'Lire',
     'Restart' : u'Lire depuis le début',
     'Delete' : u'Supprimer',
     
     'ComSkipper                      [Off]' : u'ComSkipper                      [Non]',
     'ComSkipper                       [On]' : u'ComSkipper                      [Oui]',
     #'Mark Commercials' : u'Mark Commercials',
     #"Mark Commercials    [Running]" : u"Mark Commercials    [Running]",
     
     'Delete Recording(s):' : u'Supprimer Enregistrement(s):',
     'Are you sure you want to delete %d recordings from %s?' : u'Confirmez-vous la suppression de %d enregistrements de la série %s?',
     'Are you sure you want to delete' : u'Confirmez-vous la suppression de',
     
     'Launching EyeTV' : u'Commencer EyeTV',
     'Now Recording' : u"Maintenant enregistrant!",
     "Currently recording channel %s.  Program info is not available." : u"Maintenant enregistrant: %s.  L'information de programme n'est pas disponible.",

     'Episode' : u'Épisode',
     'Channel' : u'Chaîne',
     'Position' : u'Position',
     'Recorded at' : u'Enregistrées à',
     "Next" : u"Prochain",
     "At" : u"À"
     },

    'nl': # Dutch
      {'Yes' : u'Ja',
       'No'  : u'Nee',
     
       'Recordings by Series' : u'Gesorteerde opnames',
       'Favorite Channels' : u'Favoriete zenders',
       'All Channels' : u'Alle zenders',
       'Program Guide' : u'Programma gids',
     
       'Delete All' : u'Alle verwijderen',
       'Play' : u'Afspelen',
       'Restart' : u'Herstarten',
       'Delete' : u'Verwijderen',
     
       'Delete Recording(s):' : u'Verwijder opname(s):',
     
       'Are you sure you want to delete %d recordings from %s?' : u'Weet u zeker dat u %d opname(s) van %s wilt verwijderen?',
       'Are you sure you want to delete' : u'Weet u zeker dat u',
     
       'ComSkipper                      [Off]' : u'ComSkipper [Nee]',
       'ComSkipper                       [On]' : u'ComSkipper [Ja]',
       #'Mark Commercials' : u'',
       #"Mark Commercials    [Running]" : u"Mark Commercials    [Running]",

       #'Launching EyeTV' : u'',
       #'Now Recording' : u'',
       #"Currently recording channel %s.  Program info is not available." : u'',

       'Episode' : u'Aflevering',
       'Channel' : u'Zender',
       'Position' : u'Positie',
       'Recorded at' : u'Opgenomen op',
       "Next" : u'Volgende',
       "At" : u'Om'
       },

# 'xx':
#      {'Yes' : u'',
#       'No'  : u'',
      
#       'Recordings by Series' : u'',
#       'Favorite Channels' : u'',
#       'All Channels' : u'',
#       'Program Guide' : u'',
      
#       'Delete All' : u'',
#       'Play' : u'',
#       'Restart' : u'',
#       'Delete' : u'',
      
#       'Delete Recording(s):' : u'',
      
#       'Are you sure you want to delete %d recordings from %s?' : u'',
#       'Are you sure you want to delete' : u'',
      
#       'ComSkipper                      [Off]' : u'',
#       'ComSkipper                       [On]' : u'',
#       #'Mark Commercials' : u'',
#       #"Mark Commercials    [Running]" : u'',


#       'Launching EyeTV' : u'',
#       'Now Recording' : u'',
#       "Currently recording channel %s.  Program info is not available." : u'',
      
#       'Episode' : u'',
#       'Channel' : u'',
#       'Position' : u'',
#       'Recorded at' : u'',
#       "Next" : u'',
#       "At" : u''

#       },

 }


def tr(str,comment=''):
    if languageCode=='en' or not translations.has_key(languageCode) or not translations[languageCode].has_key(str):
        return str
    return translations[languageCode][str]


