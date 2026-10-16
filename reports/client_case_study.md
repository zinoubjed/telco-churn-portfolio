# Telco Churn — Étude de cas pour prospects

**Nature du projet :** simulation de mission sur le jeu de données public IBM Telco Customer Churn. Ce n'est pas une mission effectuée pour un client réel, ni un déploiement en entreprise.

## Problème métier simulé
Une équipe fidélisation doit prioriser les clients à examiner avec une capacité de contact limitée. Objectif : mesurer si un classement du risque peut aider à comparer des politiques de contact. Budget, décideur, coût des erreurs et efficacité des offres restent inconnus.

## Travaux réalisés dans le projet
- Diagnostic de la qualité et provenance des données : 7 043 clients, 21 colonnes, 11 valeurs TotalCharges inconnues conservées.
- EDA décisionnelle sur entraînement, notamment contrat et ancienneté, sans conclusion causale.
- Préparation avec séparation train / validation / test : 4 225 / 1 409 / 1 409 ; transformations apprises dans le pipeline.
- Comparaison Dummy, régression logistique et Random Forest ; contrôles de reproductibilité et de fuite de préparation.
- Traduction des scores en volumes, précision, rappel, faux positifs et faux négatifs.
- Restitution par notebook, note métier, méthodologie et tableau de bord interactif.

## Résultats observés sur données pédagogiques
- 1 869 churners observés sur 7 043 clients (26,5 %).
- Régression logistique : ROC-AUC test environ 0,843.
- Top 10 % : 141 clients signalés, dont 105 churners ; précision 74,5 %, rappel 28,1 %.
- Top 30 % : 423 clients signalés, dont 246 churners ; précision 58,2 %, rappel 65,8 %.

Ces résultats mesurent un classement du risque, **pas** des clients effectivement retenus grâce à une campagne.

## Recommandation
🟢 PROMETTEUR pour une démonstration analytique reproductible. 🟡 À VALIDER pour les coûts, les dates de disponibilité des variables, la représentativité et la capacité réelle. 🔴 STOP pour une campagne opérationnelle tant que la décision et l'effet incrémental d'une intervention ne sont pas établis.

**Contre-exemple :** un client à risque élevé peut ne répondre à aucune offre, tandis qu'un client à risque modéré pourrait être retenu. Prédire le churn n'est pas mesurer l'effet d'une action.

## Pièces consultables
- [Notebook exécuté](../notebooks/telco_churn.ipynb)
- [Note de décision](business_summary.md)
- [Méthodologie](../docs/methodology.md)
- [Documentation des données](../data/README.md)
- [Tableau de bord interactif](https://zinoubjed.github.io/telco-churn-portfolio/dashboard/)

## Portée et traçabilité
Ce cas montre une démarche, des calculs et des livrables inspectables. Il ne constitue pas une preuve de mission client passée, de ROI réalisé, de déploiement ni de certification de compétence. Le projet a bénéficié d'une assistance technique et rédactionnelle ; les résultats critiques doivent rester vérifiables. Toute utilisation avec des données client exige autorisation, cadrage et validation spécifiques.

**Statut : WORKING — P1.**