# Satellite Tracker Web App
## Description

Une application web interactive pour visualiser les satellites en orbite terrestre.
Elle utilise les données TLE pour calculer les positions et fournit un globe 3D interactif, des statistiques et des détails pour chaque satellite.

## Fonctionnalités principales

- Globe 3D interactif avec CesiumJS, satellites colorés selon leur classe orbitale

- Statistiques et graphiques sur la répartition par altitude, type et orbite

- Détails des satellites : TLE, altitude, type d’orbite, latitude et longitude

- Recherche avancée avec filtres par nom, type et orbite

- API RESTful pour récupérer les données satellites (liste complète et détail d’un satellite)

## Installation avec Docker

1. Cloner le projet :
```git clone https://github.com/skayne11/BigDataCloud.git```
```cd BigDataCloud```

2. Construire l’image Docker :
```docker build -t BigDataCloud .```

3. Lancer le conteneur :
```docker run -p 5000:5000 BigDataCloud```

4. Ouvrir l’application dans le navigateur :
http://127.0.0.1:5000

## Pages principales

- / : Accueil avec le globe 3D interactif

- /search : Recherche de satellites avec filtres par nom, type et orbite

- /satellite/<name> : Détails d’un satellite : TLE, altitude, orbite, latitude/longitude

- /api/satellites : Endpoint JSON pour toutes les positions satellites

- /api/satellite/<name> : Endpoint JSON pour un satellite précis

## Architecture du projet

- templates/ : Pages HTML Flask

    - base.html

    - globe.html

    - search.html

    - satellite_detail.html

- static/

    - css/ : style.css

    - js/ : globe.js

- app.py : Application Flask

- parse_tle.py : Parser TLE → calcul position

- Dockerfile : Conteneurisation de l’application

- README.md

## Fonctionnement

- Les TLE sont stockées dans MongoDB

- L’API Flask récupère ces données

- La librairie sgp4 calcule latitude, longitude et altitude à partir des TLE

- CesiumJS affiche le globe 3D avec les satellites colorés selon leur classe orbitale

- Les pages de recherche et de détails permettent d’explorer chaque satellite et ses informations

## Dépendances frontend

- CesiumJS pour le globe 3D interactif

- Chart.js pour les graphiques statistiques

- CSS personnalisé dans static/css/style.css

## Informations importantes

- Les coordonnées des satellites sont calculées depuis le TLE pour un instant donné et évoluent en temps réel

- L’altitude est affichée en kilomètres

- Les graphiques reflètent l’état actuel des satellites depuis l’API

## Auteur

Skayne – GitHub : https://github.com/skayne11/

Licence

MIT License