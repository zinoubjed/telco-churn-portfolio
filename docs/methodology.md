# Methodology and limitations

## Protocol

Nettoyage déterministe du format, contrôle du fichier par empreinte, conservation des 11 montants inconnus. Séparation stratifiée avec seed 42 : 4 225 train, 1 409 validation et 1 409 test. Les index sont contrôlés comme disjoints. L'EDA graphique porte sur l'entraînement.

Le pipeline apprend imputation, standardisation et catégories uniquement sur entraînement, y compris à l'intérieur des cinq plis de validation croisée. `customerID` et `Churn` sont exclus des prédicteurs. La logistique utilise max_iter=3 000 avec standardisation ; une ConvergenceWarning arrête l'exécution. La forêt utilise 200 arbres et min_samples_leaf=5, paramètres fixes et non optimisés. Le Dummy à probabilité constante et classe majoritaire sert de référence.

Le modèle est choisi selon la ROC-AUC moyenne de validation croisée d'entraînement. Un seuil correspondant au quantile 70 % des scores de validation est fixé avant l'évaluation test. Il est appliqué au modèle entraîné sur train, sans réentraînement sur validation ; ainsi le seuil et les scores restent compatibles. Le test compare aussi 0,5 et 0,4 comme scénarios explicatifs, sans choisir un nouveau seuil. Les capacités top 10/20/30 % sont déclarées dans le code et servent de diagnostics.

## Lecture des indicateurs

ROC-AUC : qualité globale du classement. Average precision : synthèse précision-rappel, pertinente pour une cible minoritaire ; elle n'est pas l'intégrale trapézoïdale de la courbe PR. Brier : erreur quadratique des probabilités (plus faible est meilleur). Précision : part de churners parmi les signalés. Rappel : part des churners signalés. La matrice est ordonnée TN, FP, FN, TP dans les exports.

L'intervalle de ROC-AUC à 95 % est un bootstrap percentile de 1 000 rééchantillonnages du test, modèle fixé. Il ne mesure ni l'incertitude d'entraînement, ni la dérive future, ni une différence statistique entre modèles. L'écart-type des plis n'est pas un intervalle de confiance. La courbe de calibration est un diagnostic, pas une certification.

## Interprétation

`reports/logistic_coefficients.csv` fournit tous les coefficients. Les numériques sont standardisés ; les indicateurs catégoriels sont one-hot. Avec catégories complètes, régularisation et variables corrélées, le signe d'un coefficient dépend du codage et des autres variables. Ce sont des associations conditionnelles, pas des effets causaux ni une preuve qu'une offre agira sur le churn.

## Limites et portée

Dataset pédagogique, un seul partage aléatoire, pas de validation temporelle/externe, pas de tuning exhaustif, pas d'analyse complète d'équité, ni d'effet causal d'intervention. La disponibilité prospective des variables reste inconnue. Les métriques test sont exposées pour revue ; toute future optimisation à partir de ces résultats nécessitera un nouveau holdout. Aucun modèle de production ou gain commercial n'est revendiqué.
