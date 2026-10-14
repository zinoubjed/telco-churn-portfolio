# Provenance et contrat de données

Source utilisée dans le travail d'origine : [IBM — Telco Customer Churn](https://github.com/IBM/telco-customer-churn-on-icp4d).
Le téléchargement reproductible pointe vers le [CSV au commit 1fd6fd7](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/1fd6fd70906479be1712e64cfc0ea89f58466629/data/Telco-Customer-Churn.csv), plutôt que vers une branche mutable.

SHA-256 des octets téléchargés :
`16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`.

Le fichier est téléchargé dans `data/raw/`, vérifié avant lecture et exclu de Git. Aucune donnée originale n'est modifiée. Les droits et conditions de la source doivent être examinés avant réutilisation commerciale ; le dépôt IBM indique Apache-2.0 pour son code pattern, ce qui ne constitue pas ici une nouvelle licence sur les données.

7 043 lignes, 21 colonnes, un identifiant unique par client. La cible `Churn` contient 1 869 Yes et 5 174 No. Le dataset pédagogique ne fournit ni horodatage individuel, ni historique longitudinal, ni résultat d'une intervention de rétention. La population et l'horizon de production ne peuvent pas être validés à partir de ce fichier.

| Groupe | Colonnes | Traitement |
|---|---|---|
| Identifiant | customerID | Exclu des variables prédictives et des exports |
| Cible | Churn | Yes = 1, No = 0 ; exclue de X |
| Numériques | tenure, MonthlyCharges, TotalCharges | Ancienneté en mois ; montants sans devise validée dans ce projet ; imputation médiane et standardisation apprises sur entraînement |
| Profil | gender, SeniorCitizen, Partner, Dependents | Catégorielles, dont SeniorCitizen codé 0/1 ; usage pédagogique à réexaminer pour une campagne |
| Téléphonie | PhoneService, MultipleLines | Catégories conservées, y compris No phone service |
| Internet et options | InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies | Catégories conservées, y compris No internet service |
| Contrat et facturation | Contract, PaperlessBilling, PaymentMethod | Encodage one-hot appris sur entraînement |

Les 11 blancs de `TotalCharges` correspondent à `tenure=0`. Ils sont conservés comme valeurs inconnues, puis imputés dans chaque pipeline ; un indicateur de valeur manquante est ajouté. Zéro serait une hypothèse comptable, pas une valeur observée. Le nombre de lignes reste identique à toutes les étapes. Les catégories inconnues sont acceptées à l'inférence. Un changement de fichier ou du motif de données manquantes déclenche une erreur explicite.
