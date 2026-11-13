# Git et GitHub

Cette note décrit la façon de travailler sur le dépôt : les branches, les commits, les pull requests et les réglages à faire sur GitHub.

## Stratégie de branches

Le projet suit le **GitHub Flow** :

- `main` est toujours stable et déployable ;
- chaque changement se fait sur une branche courte, créée depuis `main` ;
- la branche revient dans `main` par une pull request, une fois la CI au vert ;
- la branche est supprimée après la fusion.

### Pourquoi ce choix

C'est le fonctionnement le plus répandu en entreprise pour les applications web, et il reste léger pour un développeur seul.

- **La pull request sert de point de contrôle**, même sans relecteur : c'est là que la CI tourne, et relire son propre diff avant de fusionner fait trouver des erreurs.
- **`main` ne casse jamais** : un travail en cours ou raté reste sur sa branche.
- **L'historique reste lisible** : avec la fusion en *squash*, une pull request donne un seul commit sur `main`.

Le modèle Git Flow (branches `develop`, `release`, `hotfix`) n'a pas été retenu. Il est conçu pour des logiciels livrés par versions numérotées, avec plusieurs versions maintenues en parallèle. Ici, il ajouterait des branches à synchroniser sans rien apporter.

### Nommer les branches

| Préfixe | Usage | Exemple |
|---|---|---|
| `feat/` | nouvelle fonctionnalité | `feat/creation-seance` |
| `fix/` | correction de bug | `fix/calcul-volume` |
| `chore/` | outillage, configuration, maintenance | `chore/mise-a-jour-django` |
| `docs/` | documentation | `docs/guide-installation` |

Le nom est en minuscules, sans accents, avec des tirets.

## Convention de commits

Un message de commit est court, en français, à l'impératif présent, et commence par un préfixe :

| Préfixe | Usage |
|---|---|
| `feat:` | ajoute une fonctionnalité |
| `fix:` | corrige un bug |
| `chore:` | outillage, configuration, dépendances |
| `docs:` | documentation |

```
feat: ajoute la création d'une séance
fix: corrige le calcul du volume total
chore: met à jour Django
docs: complète le guide d'installation
```

Les messages ne contiennent pas de ligne `Co-Authored-By`.

Avec la fusion en *squash*, c'est le **titre de la pull request** qui devient le message du commit sur `main`. C'est donc lui qui doit respecter la convention avant tout. Les commits intermédiaires d'une branche disparaissent à la fusion.

## Cycle de travail

```powershell
# 1. Partir d'un main à jour
git switch main
git pull

# 2. Créer la branche
git switch -c feat/creation-seance

# 3. Travailler, puis commiter (ruff s'exécute à chaque commit)
git add .
git commit -m "feat: ajoute la création d'une séance"

# 4. Pousser la branche
git push -u origin feat/creation-seance
```

Ensuite, sur GitHub :

1. ouvrir la pull request vers `main`, avec un titre qui suit la convention ;
2. attendre que les deux vérifications de la CI, `Lint` et `Tests`, soient vertes ;
3. relire le diff ;
4. fusionner avec **Squash and merge**.

Puis revenir en local :

```powershell
git switch main
git pull
git branch -d feat/creation-seance
```

Si ruff modifie un fichier pendant un commit, le commit est annulé. Il suffit de refaire `git add .` puis `git commit`.

## Mettre le dépôt sur GitHub

**1. Créer le dépôt** sur GitHub, vide : sans README, sans `.gitignore`, sans licence. Ces fichiers existent déjà en local.

**2. Relier le dépôt local et pousser `main` :**

```powershell
git remote add origin <url-du-depot>
git push -u origin main
```

**3. Pousser la branche de mise en place et ouvrir la première pull request :**

```powershell
git push -u origin chore/initialisation-projet
```

GitHub propose alors d'ouvrir la pull request. Lui donner pour titre `chore: initialise le projet`. La CI se lance : c'est sa première exécution.

## Réglages du dépôt

À faire une fois, dans l'onglet **Settings** du dépôt.

### Fusion des pull requests

Dans **General**, section **Pull Requests** :

- cocher **Allow squash merging**, et choisir **Pull request title** comme message par défaut ;
- décocher **Allow merge commits** et **Allow rebase merging** ;
- cocher **Automatically delete head branches**.

Une seule façon de fusionner reste possible, l'historique de `main` contient un commit par pull request, et les branches fusionnées sont supprimées toutes seules.

### Protection de `main`

Dans **Rules > Rulesets**, créer un ruleset de type *branch* :

- **Enforcement status** : Active ;
- **Target branches** : la branche par défaut (`main`).

Règles à cocher :

| Règle | Effet |
|---|---|
| **Restrict deletions** | `main` ne peut pas être supprimée |
| **Block force pushes** | l'historique de `main` ne peut pas être réécrit |
| **Require a pull request before merging** | plus aucun commit direct sur `main` |
| **Require status checks to pass** | la fusion est bloquée tant que la CI n'est pas verte |

Précisions :

- pour **Require a pull request**, laisser le nombre d'approbations requises à **0** : seul sur le projet, on ne peut pas approuver sa propre pull request ;
- pour **Require status checks**, ajouter les deux vérifications `Lint` et `Tests`. Elles n'apparaissent dans la liste qu'après une première exécution de la CI : il faut donc ouvrir la première pull request **avant** de faire ce réglage.

### Limite de l'offre gratuite

Sur un compte GitHub gratuit, la protection de branche n'est appliquée que sur les dépôts **publics**. Sur un dépôt privé, les règles peuvent être créées mais ne sont pas appliquées sans passer à l'offre payante. Dans ce cas, la discipline reste la même, mais elle repose sur vous : ne jamais pousser directement sur `main`.
