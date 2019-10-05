# RRFSentinel
La RRFSentinel a pour mission de veiller au bon fonctionnement du réseau RRF en luttant contre les déclenchements intempestifs.

## Définition d'un déclenchement intempestif

Un déclenchement intempestif est un passage en émission dont la durée est inférieure à 3 secondes. Cette durée semble donner les meilleurs résultats. À ce titre,

- une durée plus élévée générait trop de faux positifs, par exemple, un OM se signalant lors d'un blanc pour entrer dans un QSO, une séquence DTMF, etc.
- une durée moins élévée générait trop de faux négatifs, par exemple, un simple coup de pédale avec une queue de squelch un peu longue.

## Fonctionnement de la RRFSentinel

La RRFSentinel fonctionne de concert avec le RRFTracker. Ce dernier collecte tout un tas d'informations dont, entre autres, les déclenchements intempestifs (indicatif du link, horodatage, décompte, etc.).

La RRFSentinel utilise donc les informations collectées par le RRFTracker. Elle va les analyser et appliquer des règles de bannissement si nécessaire.

### Une règle générique

La RRFSentinel applique une règle générique qui, si elle est vérifiée, entrainera une action de banissement. Cette règle peut être énnoncée ainsi: à partir d'une nombre N de déclenchements intempestifs dans une laps de temps L, un bannissement sera appliqué au link responsable pour une durée D.

Aujourd'hui, le nombre N est égal à 4 et le laps de temps L a été fixé à 5 minutes.

### Un bannissement variable

#### Fair use N°1

La durée de bannissement est fixée à 5 minutes entre 00:00 AM et 06:00 AM. 

#### Fair use N°2

À partir de 06:00 AM, la durée de bannissement est toujours fixée à 5 minutes mais uniquement lors des 3 premiers bannissement.

#### Plus un link perturbe le RRF, plus longtemps il sera banni

Au délà, la durée de bannissement est fixée au nombre de déclenchements intempestifs mesuré depuis le début de la journée multiplié par 2 ! 

## Mise en oeuvre

Il est possible de lancer et arréter la RRFSentinel de la facon suivante. Sur les serveur 1 et 3 :

```
/opt/RRFSentinel/RRFSentinel_RRF.sh start
/opt/RRFSentinel/RRFSentinel_RRF.sh stop
```

## Monitoring

Il est possible de suivre l'activité de la RRFSentinel dans la journée, via un script prévu à cet effet.

```
/opt/RRFSentinel/stats.py
```

Pour consulter l'activité sur une autre journée, il suffit d'indiquer la date en argument :

```
/opt/RRFSentinel/stats.py --day YYYY-MM-DD
```