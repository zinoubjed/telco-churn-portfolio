# Telco Churn — du score à une décision défendable

**Zaineb Mhiri · étude personnelle de portfolio**

[English](README.md) · [Notebook exécuté](notebooks/telco_churn.ipynb) · [Synthèse métier](reports/business_summary.md) · [Méthode](docs/methodology.md)

Comment examiner une priorisation de contacts lorsque la capacité de fidélisation est limitée ? Le projet relie contrôle des données, modèles simples et volumes d'erreurs. Il montre aussi pourquoi des données propres et un score informatif ne suffisent pas à décider d'une campagne.

![Dashboard Telco — capacité de 30 pour cent sur le test](figures/dashboard_capture.jpg)

## Démarche et livrables

Besoin → Gate 0 → DPD → compréhension → nettoyage → EDA décisionnelle → préparation → baseline/ML facultatif → évaluation/MRT → interprétation → recommandation → vérification.

Chaque opération importante du notebook suit HL : contexte, question, notion, risques, mesure, code, lecture, interprétation, impact et trace. Les retours au cadrage, au nettoyage ou à la préparation sont possibles lorsqu'une anomalie ou une fuite apparaît.

Le dépôt fournit un notebook exécuté, des métriques traçables, une synthèse métier, un dashboard interactif hors ligne et sa capture. Ce projet personnel a bénéficié d'une révision technique assistée. Il ne représente ni une mission client, ni une campagne déployée, ni une certification de compétence professionnelle.

## Gate 0 et DPD

Le scénario est une équipe CRM souhaitant étudier qui contacter. Le client réel, le décideur, le budget, les coûts FP/FN et l'effet d'une offre ne sont pas connus. La date de scoring et l'horizon ne sont pas établis.

Le pipeline protège contre les fuites techniques de préparation. La disponibilité des variables avant churn et la représentativité d'une clientèle future ne sont pas vérifiables dans ce fichier.

**Verdict : classement prometteur pour une étude ; STOP déploiement.** Poursuivre uniquement après cadrage client, validation temporelle et mesure de l'effet incrémental d'une campagne.

## Résultats vérifiés

Source IBM figée et vérifiée : **7 043 clients**, dont **1 869 churners (26,5 %)**. Les 11 montants inconnus sont conservés puis imputés sur entraînement. Split : 4 225 train, 1 409 validation, 1 409 test, seed 42.

La logistique est sélectionnée selon l'AUC moyenne en validation croisée sur train : 0,848 contre 0,847 pour la forêt. Son AUC test est de **0,843**. Les modèles sont proches, et la forêt a une average precision test légèrement meilleure.

À capacité top 30 %, **423 contacts** incluent **246 churners observés** : précision **58,2 %**, rappel **65,8 %**. Le seuil fixé sur validation pour environ 30 % signale 32,1 % du test : un seuil fixe ne garantit pas une capacité constante.

TP signifie client au churn observé correctement signalé, pas client sauvé. Aucun ROI n'est démontré. Une population à haut risque peut être moins réceptive à une offre qu'une population à risque modéré.

## Présentation pour les prospects

[**Consulter l’étude de cas professionnelle**](reports/client_case_study.md) : besoin métier simulé, travaux réalisés, résultats mesurés, recommandations et limites. Ce projet sur données publiques IBM n’est pas une mission effectuée pour un client réel et ne démontre ni déploiement ni ROI de campagne.

## Consulter et reproduire

Pour consulter les résultats sur GitHub, ouvrir le notebook et la synthèse. Le [dashboard interactif](https://zinoubjed.github.io/telco-churn-portfolio/dashboard/) est prévu pour une consultation directe sur GitHub Pages. Il peut aussi être utilisé hors ligne : télécharger le dépôt et ouvrir [dashboard/index.html](dashboard/index.html) dans un navigateur.

Les instructions Python et la comparaison complète sont dans [le README principal](README.md). Installation séparée Python 3.10, exécution intégrale du notebook, trois tests ciblés, empreinte des données et interactions du dashboard ont été vérifiés.

Les limites restent explicites : pas de test temporel ou externe, pas d'effet d'offre mesuré, pas d'audit exhaustif d'équité. La publication n'atteste pas automatiquement la maîtrise professionnelle du travail.
