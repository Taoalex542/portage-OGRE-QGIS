ce fichier txt est un readme documentant comment créer un controle et comment marche le système des controles ainsi que les interactions avec QGIS

pour ce plugin, un controle est composé de 3 fichiers:
	- le controle en soi (ctrl_exemple.py)
	- le fichier de communiquation avec QGIS (exemple.py)
	- le fichier de paramètres (param.txt)

pour faire un nouveau controle, il suffit de remplacer le mot exemple présent dans ces fichier ainsi que leur nom et ils seront utilisables automatiquement

pour appeler ce controle dans le lancement des controles du plugin, il suffit d'ajouter ces deux lignes de code dans la fonction run_controls() située dans le fichier SHREC.py:
        if ("exemple.py" in self.loaded_controles and "ctrl_exemple.py" in self.loaded_controles):
            exemple.exemple(self, ctrl_exemple.ctrl_exemple)


la suite de ce fichier txt parlera du quel fichier fait quoi, et de choses importantes à savoir sur l'utilisation de ces fichiers

param.txt :
ce fichier est le fichier de paramètres, il contient 4 lignes obligatoires, le reste des lignes seront considérées en tant que paramètres
la ligne 1 définit si le contrôle est pour une réconcilliation si une erreur trouvée par ce contrôle est présente
la ligne 2 définit si le controle doit etre lancé au moins une fois avant de pouvoir réconcillier
la ligne 3 est l'importance du contrôle, avec 0 étant le plus important, et plus le chiffre est élevé, moin le contrôle est important
la ligne 4 définit si le controle est activé ou non au lancement du plugin
chaque ligne après la ligne 4 peut etre utilisée en tant que paramètre pour le controle
si il manque l'une des 4 lignes obligatoires, le plugin utilisera les valeurs par défaut (0, 0, 10000, 1 respectivement) et avertira l'utilisateur du problème


ctrl_exemple.py :
le fichier controle est le "moteur" du contrôle, il contient la ou se fera le controle quand il sera éxécuté
il est important de noter que ce fichier est le seul moment ou les calculs se feront
le controle récupère les information de la géométrie (dans le cas de l'exemple, appelé data)
il peut aussi récuperer une deuxième géométrie ou des paramètres comme dans le contrôle sur les attributs
il suffit de les ajouter dans les paramètres de fonction et de bien les envoyer dans le fichier python exemple.py quand ctrl_exemple est 
la fonction ctrl_exemple renvoie un tableau de tuple de coordonnées (x et y) contenant ou les erreurs sont trouvée, si aucune erreur est presente, renvoie un tableau vide
ATTENTION: si autre chose qu'un tuple de coordonnée est ajoutée dans le tableau, la fonction de lien avec QGIS (ici exemple(self, func)) crashera
l'utilisateur est libre de faire ce qu'il veut en tant que controle, tant que ce controle renvoie seulement un tableau de tuples


exemple.py :
ce fichier est ce qui permet au contrôle de communiquer avec le plugin et QGIS, il est composé en deux parties principales: la fonction read() et la fonction exemple()

read() lit le fichiers param.txt et récupère les paramètres entrés.
actuellement il récupère le chiffre entré avec un regex, et vérifie si il n'est pas plus grand que 50
si le chiffre entré est plus grand que 50, il renvoie la valeur par défaut (ici 10)
cette fonction peut lire et extraire autant de paramètres que possible, il suffit juste d'écrire une fonction pour les récuperer
il est important de noter que les paramètres du controle doivent commencer à la 4eme ligne et non avant à cause le la lecture des paramètre de profil du contrôle
chaque contrôle peut avoir une gestion de parametrage unique

exemple() est la fonction qui parcours les couches et les controles unes par unes
actuellement, cette fonction ne regarde seulement les couches de type lignes, pour changer cela, il suffit de modifier "if ("LineString" not in QgsWkbTypes.displayString(part.wkbType())):" dans la fontion exemple() et la fonction get_quantity()
il existe 3 types de géométrie:
    - Point
    - LineString
    - Polygon
il est possible d'enlever cette condition et de travailler sur toutes les couches au lieu de juste certains types
la fonction ne travaille que sur les objerts séléctionnés si il en existe.
si une erreur est trouvée, la fonction édite la couche des points de controles et y ajoute le nouveau controle.