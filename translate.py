import Foundation
# -*- coding: utf-8 -*-

languageCode=Foundation.NSUserDefaults.standardUserDefaults().objectForKey_('AppleLanguages')[0]
#languageCode='da'

translations=\
{'fr':
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

 'da':
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


