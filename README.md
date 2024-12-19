<a name="top"></a>
![language](https://img.shields.io/badge/langage-python-blue)
[![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)](https://docs.abblix.com/docs/technical-requirements)
[![getting started](https://img.shields.io/badge/manuel_utilisateur-guide-1D76DB)](https://docs.abblix.com/docs/getting-started-guide)

## Table of Contents
- [À propos](#-À-propos)
- [Comment installer](#-Comment-installer)
- [Documentation](#-documentation)

## 🚀 À propos

SHREC (Système Hybride des Reconciliations, Extractions et Contrôles) est un plugin permettant de contrôler tout type de géométries chargées dans QGIS.

Les contrôles sont des contrôles portés de OGRE, un plugin Geoconcept interne à l'IGN

- **Modulaire**: Chaque contrôle du plugin fonctionne indépendamment, améliorant la modularité de la librairie et permettant une maintenance et des mises à jour plus faciles.
- **Maintenabilité Simple**: Une structure et une séparation claires facilitent une meilleure gestion de la base de code.

La librairie de contrôle permet de pouvoir utiliser ces contrôles en dehors de QGIS avec un support en Python. 

SHREC communique aussi avec le plugin [CETACE](https://gitlab.ign.fr/bduni_prod/autres-projets/cetace) et  utilise ses zones pour contrôler les géométries, comme avec les zones de réconciliations, permettant de facilement contrôler une zone.


## 📝 Comment installer le plugin sur QGIS

Il existe plusieurs façons d'installer le plugin :

### Installer depuis un fichier zip
- Créez un fichier zip et mettez le dossier SHREC dans ce fichier zip
- Vous devriez avoir un chemin de dossier tel que \SHREC.zip\SHREC
- Allez ensuite dans QGIS, dans le menu extensions, puis installez des extensions depuis un zip et sélectionnez le fichier zip.
- SHREC sera installé

### Installer le plugin manuellement
- Mettez le dossier SHREC dans l'installation des plugins QGIS
- Le chemin est C:\Users\\[nom_utilisateur]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
- Il suffit ensuite d'activer le plugin dans la fenêtre des extensions de QGIS

## 📚 Documentation 

### Pour commencer
Explorez le [manuel d'utilisateur](https://gitlab.ign.fr/bduni_prod/autres-projets/shrec/-/raw/main/Manuel%20utilisateur%20du%20plugin.docx?ref_type=heads).
Dans ce manuel, vous apprendrez chaque fonctionnalité présente dans le plugin SHREC, ainsi que comment les utiliser.

Pour mieux comprendre le fonctionnement interne du projet, , il est recommandé de lire le readme présent dans [exemple_de_controle](https://gitlab.ign.fr/bduni_prod/autres-projets/shrec/-/blob/main/exemple_de_controle/readme.txt?ref_type=heads).

Cet outil est idéal aussi bien pour les nouveaux utilisateurs que pour les utilisateurs expérimentés voulant contrôler leurs données géographiques.

[Back to top](#top)
