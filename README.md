# Bella Italia - Application microservices
## Auteurs

- Nima DAVARI
- Ghilas TIDJET

## Présentation

Bella Italia est une application distribuée basée sur une architecture microservices.  
Le projet représente une application de gestion pour un restaurant italien. Il permet de consulter le menu, créer des commandes, calculer automatiquement le total d'une commande, stocker les données dans PostgreSQL et accéder à l'application via une gateway locale avec Ingress.

Projet réalisé dans le cadre du cours de programmation distribuée.

## Fonctionnalités

- Consultation du menu du restaurant
- Création et affichage des commandes
- Calcul automatique du total d'une commande
- Communication entre microservices
- Interface web simple
- Stockage des données avec PostgreSQL
- Déploiement avec Docker et Kubernetes
- Exposition avec Ingress NGINX
- Sécurité de base avec RBAC

## Architecture

```text
Navigateur http://localhost
        |
        v
Ingress NGINX Gateway
        |----> frontend-service (/)
        |----> menu-service (/menu)
        |----> order-service (/orders)

order-service ---- appelle ----> menu-service
menu-service  ---- stocke ----> PostgreSQL
order-service ---- stocke ----> PostgreSQL
```

## Structure du projet

```text
microservices-task-project/
|-- frontend/
|-- menu-service/
|-- order-service/
|-- k8s/
|-- README.md
|-- .gitignore
```

## Technologies utilisées

- FastAPI
- Python
- PostgreSQL
- Docker
- Docker Hub
- Kubernetes
- NGINX Ingress Controller
- RBAC Kubernetes
- HTML
- CSS
- JavaScript
- Git / GitHub

## Routes principales

### Menu Service

| Méthode | Route | Description |
|---|---|---|
| GET | `/menu` | Affiche tout le menu |
| GET | `/menu/category/{category}` | Affiche les plats d'une catégorie |
| GET | `/menu/item/{id}` | Affiche un plat précis |
| POST | `/menu` | Ajoute un plat |
| PUT | `/menu/item/{id}` | Modifie un plat |
| DELETE | `/menu/item/{id}` | Supprime un plat |

### Order Service

| Méthode | Route | Description |
|---|---|---|
| GET | `/orders` | Affiche toutes les commandes |
| GET | `/orders/{id}` | Affiche une commande précise |
| POST | `/orders` | Crée une commande |
| PUT | `/orders/{id}` | Modifie une commande |
| PUT | `/orders/{id}/status` | Modifie le statut d'une commande |
| DELETE | `/orders/{id}` | Supprime une commande |
| GET | `/menu-from-service` | Teste la communication avec menu-service |

## Accès à l'application

| URL | Description |
|---|---|
| `http://localhost/` | Interface front-end |
| `http://localhost/menu` | API du menu |
| `http://localhost/orders` | API des commandes |
| `http://localhost/menu-from-service` | Test de communication entre services |

## Images Docker Hub

| Composant | Image |
|---|---|
| menu-service | `nima0d80/menu-service:latest` |
| order-service | `nima0d80/order-service:latest` |
| frontend | `nima0d80/restaurant-frontend:latest` |

## Déploiement Kubernetes

Appliquer tous les fichiers Kubernetes :

```bash
kubectl apply -f k8s/
```

Vérifier les ressources :

```bash
kubectl get pods
kubectl get services
kubectl get pvc
kubectl get ingress
```

## Base de données

PostgreSQL est utilisé comme base de données pour stocker les plats du menu et les commandes.

Service interne PostgreSQL :

```text
postgres-service:5432
```

## Sécurité RBAC

Les pods utilisent un ServiceAccount dédié :

```text
restaurant-app-sa
```

Commandes de vérification :

```bash
kubectl describe pod -l app=menu-service
kubectl describe pod -l app=order-service
kubectl describe pod -l app=restaurant-frontend
```

Le résultat doit contenir :

```text
Service Account: restaurant-app-sa
```

## Tests réalisés

| Test | Résultat |
|---|---|
| Accès au front-end | OK |
| Accès au menu via Ingress | OK |
| Accès aux commandes via Ingress | OK |
| Création d'une commande | OK |
| Calcul automatique du total | OK |
| Communication entre microservices | OK |
| Persistance PostgreSQL | OK |
| Publication Docker Hub | OK |
| Sécurité RBAC | OK |

