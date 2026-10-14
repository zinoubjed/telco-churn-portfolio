# Note de décision — prioriser une étude de rétention

**Recommandation analytique : STOP déploiement ; poursuivre une validation sur données réelles sous conditions.**
Ce projet personnel de Zaineb Mhiri montre une démarche de diagnostic, de modélisation interprétable et d'évaluation sous contrainte de capacité. Il ne décrit pas une mission client réalisée.

## Cadre de travail

Le décideur envisagé est une équipe CRM / fidélisation. Le besoin supposé est de prioriser des contacts limités. L'action envisagée est un contact de rétention sur une cohorte de clients éligibles. Aucun client réel ni brief validé n'est fourni. Ces éléments sont un scénario de démonstration, à confirmer avec le client. La capacité de 30 % est illustrative, pas un budget contractualisé.

**Gate 0 bloque l'action :** décision opérationnelle, décideur réel, risques acceptés, coûts d'erreur et option de refus doivent être cadrés. **DPD bloque la généralisation :** ni disponibilité des variables avant décision, ni représentativité, ni effet de contact ne sont attestés.

Avant de prédire un churn futur, il faut définir une date de scoring et un horizon (par exemple 30 jours, à valider), puis reconstruire chaque variable à cette date. Le fichier actuel ne permet pas de vérifier que contrats, services et montants étaient disponibles avant le départ. La séparation aléatoire teste une généralisation dans ce dataset, pas une performance prospective.

## Ce que les résultats permettent de dire

Sur 1 409 clients de test, les 10 % les mieux classés par la régression logistique contiennent 105 churners observés : précision 74,5 %, rappel 28,1 %, lift de 2,81 par rapport à un ciblage aléatoire. Cela justifie d'étudier la priorisation, pas de promettre 105 clients sauvés.

À capacité de 30 %, les 423 premiers scores contiennent 246 churners : 58,2 % de précision et 65,8 % de rappel. Un seuil fixe appris sur validation donne 452 contacts sur test, soit 32,1 %. Une campagne soumise à un plafond strict doit utiliser un classement top-k et une règle d'éligibilité, pas supposer qu'un seuil fixe maintient le même volume.

La validation croisée d'entraînement donne des ROC-AUC proches : 0,848 pour la logistique et 0,847 pour la forêt. La logistique est retenue selon cette règle préétablie, avec un intérêt d'interprétation. La forêt a une average precision légèrement meilleure sur test. Aucune supériorité générale ou limite informationnelle définitive n'est démontrée.

## Du risque au retour sur investissement

Le dataset ne renseigne ni le coût d'un contact, ni la marge future, ni l'efficacité d'une offre. TP signifie churn observé et correctement signalé ; il ne signifie pas client récupérable. FP ne signifie pas nécessairement coût faible. Un churner peut refuser toute offre.

**MRT — erreurs et contraintes :** à 0,5, la logistique signale 316 clients (205 TP, 111 FP) et manque 169 churners. À 0,4, elle signale 435 clients (250 TP, 185 FP) et manque 124 churners. Réduire le seuil ajoute 119 contacts pour 45 TP supplémentaires sur ce test. Sans coûts ni effet d'action, cette différence ne suffit pas à arbitrer. Une perte de classification illustrative peut être écrite FP × coût_FP + FN × coût_FN ; ces coûts restent à estimer et cette perte n'est pas un ROI de campagne.

Une hypothèse de valeur peut s'écrire : valeur attendue = somme des probabilités incrémentales de rétention × marges futures − coûts de contact − coûts des offres. Les probabilités incrémentales doivent venir d'un essai randomisé ou d'une estimation causale défendable, pas des scores de churn.

## Validation proposée au client

1. Définir population éligible, horizon, décideur, budget, coûts d'erreur et option de ne pas agir.
2. Vérifier les variables à la date de scoring ; réserver une période récente en test temporel.
3. Évaluer calibration, stabilité et erreurs par segments ; réexaminer l'utilité et l'équité de l'usage des variables de profil.
4. Comparer le classement à une règle CRM simple sur données opérationnelles.
5. Tester la campagne avec groupe témoin, mesurer rétention incrémentale, coût et marge, puis décider.

**Contre-exemple :** une cohorte à très haut risque peut être impossible à retenir, tandis qu'une cohorte à risque modéré répond mieux à l'offre. Maximiser le rappel du churn peut alors réduire la valeur de la campagne.

**Conditions d'arrêt :** données temporelles insuffisantes, variables indisponibles au scoring, bénéfice incrémental non positif, capacité dépassée ou écarts de traitement injustifiables. Aucun score n'autorise une action automatique sur un client.

## Trois validations distinctes

- **Technique :** exécution, reproductibilité, contrôles et traçabilité font l'objet de la revue de cette version.
- **Décisionnelle :** le benchmark est informatif ; la décision opérationnelle reste bloquée par Gate 0 et DPD.
- **Orale :** Zaineb doit pouvoir expliquer les choix, risques, contre-exemple et recommandation avant présentation à un client. Cette capacité n'est pas validée automatiquement.

Les anomalies peuvent conduire à revenir au nettoyage, une fuite à la préparation, une évolution des coûts à Gate 0. Cette étude personnelle constitue un exemple analytique ; elle ne représente pas une mission client ni une validation de compétence professionnelle.
