# RRFSentinel
La RRFSentinel a pour mission de veiller au bon fonctionnement du réseau RRF en luttant contre les déclenchements intempestifs.

## Définition d'un déclenchement intempestif

Un déclenchement intempestif est un passage en émission dont la durée est inférieure à 3 secondes. Cette durée semble donner les meilleurs résultats. À ce titre,

- une durée plus élévée générait trop de faux positifs, par exemple, un OM se signalant lors d'un blanc pour entrer dans un QSO, une séquence DTMF, etc.
- une durée moins élévée générait trop de faux négatifs, par exemple, un simple coup de pédale avec une queue de squelch un peu longue.

## Fonctionnement de la RRFSentinel

La RRFSentinel fonctionne de concert avec le RRFTracker. Ce dernier collecte tout un tas d'informations dont, entre autres, les déclenchements intempestifs (indicatif du link, horodatage, décompte, etc.).

La RRFSentinel utilise donc les informations collectées par le RRFTracker. Elle va les analyser et appliquer des règles de mise en quarantaine si nécessaire.

### Une règle générique

La RRFSentinel applique une règle générique qui, si elle est vérifiée, entrainera une action de mise en quarantaine. Cette règle peut être énnoncée ainsi: à partir d'une nombre N de déclenchements intempestifs dans une laps de temps L, une mise en quarantaine sera appliquée au link responsable pour une durée D.

Aujourd'hui, le nombre N est égal à 4 et le laps de temps L a été fixé à 5 minutes.

### Une mise en quarantaine variable

#### Fair use N°1

La durée de mise en quarantaine est fixée à 5 minutes entre 00:00 AM et 06:00 AM. 

#### Fair use N°2

À partir de 06:00 AM, la durée de mise en quarantaine est toujours fixée à 5 minutes mais uniquement lors des 3 premières fois.

#### Plus un link perturbe le RRF, plus longtemps il sera placé en quarantaine

Au délà, la durée de mise en quarantaine est calculée ainsi :

- pour un link : (nombre de déclenchements intempestifs depuis le début de la journée) x 2
- pour un hotspot : (nombre de déclenchements intempestifs depuis le début de la journée) x (nombre de mises en quarantaine - 3)

## Mise en oeuvre

Il est possible de lancer et arrêter la RRFSentinel de la facon suivante. Sur les serveur 1, 2 et 3 :

```
/opt/RRFSentinel/RRFSentinel.sh start
/opt/RRFSentinel/RRFSentinel.sh stop
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