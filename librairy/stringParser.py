#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import expanduser
from workWithModule import workWithModule
from basicCommands import basicCommands
from Googletts import tts
import xml.etree.ElementTree as ET
import os, gettext, time, sys, subprocess

# Permet d'exécuter la commande associée à un mot prononcé
class stringParser():
    """
    @description: This class parses the text retrieve by Google in order 
    to distinguish external commands, internal commands and modules
    """
    def __init__(self,text,File,PID):
        # read configuration files
        self.pid=PID
        try:
            max = 0
            text=text.lower()
            tree = ET.parse(File)
            root = tree.getroot()
            tp = ''
            # si le mode dictée est activé
            if os.path.exists('/tmp/g2u_dictation'):
                for entry in root.findall('entry'):
                    if entry.get('name') == _('internal') and entry.find('command').text == unicode(_('exit dictation mode'),"utf8"):
                        score = 0
                        Type=entry.get('name')
                        Key=entry.find('key').text
                        Command=entry.find('command').text
                        key=Key.split(' ')
                        for j in range(len(key)):
                            score += text.count(key[j])
                        
                        if score == len(key):
                            do = Command
                            tp = Type
                        else:
                            do = text
            else:
                for entry in root.findall('entry'):
                    score = 0
                    Type=entry.get('name')
                    Key=entry.find('key').text
                    Command=entry.find('command').text
                    key=Key.split(' ')
                    for j in range(len(key)):
                        score += text.count(key[j])
                        
                    if max < score:
                        max = score
                        do = Command
                        tp = Type
            
            # on regarde si la commande fait appel à un module
            # si oui, alors on lui passe en paramètre les dernier mots prononcé
            # ex: si on prononce "quelle est la météo à Paris"
            # la ligne de configuration dans le fichier est: [q/Q]uelle*météo=/modules/weather/weather.sh
            # on coupe donc l'action suivant '/'
            do=do.encode('utf8') 
            tp=tp.encode('utf8')
            print tp, do
            os.system('echo "'+do+'" > /tmp/g2u_cmd_'+self.pid)
            if _('modules') in tp:
                check = do.split('/')
                # si on trouve le mot "modules", on instancie une classe workWithModule et on lui passe
                # le dossier ie weather, search,...; le nom du module ie weather.sh, search.sh et le texte prononcé
                wm = workWithModule(check[0],check[1],text,self.pid)
            elif _('internal') in tp:
                # on execute une commande intene, la commande est configurée
                # ainsi interne/batterie, on envoie batterie à la fonction
                b = basicCommands(do,self.pid)
            elif _('external') in tp:
                os.system(do)
            else:
                os.system('xdotool type "'+do+'"')
                
            os.system('> /tmp/g2u_stop_'+self.pid)
            
            
        except Exception as e:
            message = _('Setup file missing')
            os.system('echo "'+message+'" > /tmp/g2u_error_'+self.pid)
            sys.exit(1)   
