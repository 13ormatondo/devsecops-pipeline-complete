# 🔐 DevSecOps Pipeline - Projet Portfolio

## ✅ Statut du projet
![Jenkins Build](https://img.shields.io/badge/build-passing-brightgreen)
![SonarQube Quality Gate](https://img.shields.io/badge/quality_gate-passed-brightgreen)

## 🎯 Objectif
Pipeline CI/CD complète intégrant la sécurité à chaque étape : Threat Modeling, SAST, DAST.

## 🏗️ Architecture

| Composant | Rôle | Accès |
|-----------|------|-------|
| Jenkins | Orchestration CI/CD | http://localhost:8080 |
| SonarQube | SAST (analyse statique) | http://localhost:9000 |
| OWASP ZAP | DAST (scan dynamique) | Rapport HTML |
| Postman/Newman | Tests API sécurité | Automatisé |
| IriusRisk | Threat Modeling | SaaS |
| Application | Flask vulnérable | http://localhost:5000 |

## 🔥 Vulnérabilités identifiées

| Vulnérabilité | Endpoint | Détection |
|---------------|----------|-----------|
| SQL Injection | POST /login | SonarQube + ZAP |
| Command Injection | GET /ping | SonarQube + ZAP |
| XSS | GET / | SonarQube |
| IDOR | GET /user/{id} | ZAP |

## 🧠 Threat Modeling (IriusRisk)

> 📄 **[Télécharger le rapport complet IriusRisk (PDF)](docs/vulnerable-app-pipeline-risk-controls-summary-and-evidence-report.pdf)**

## 📊 Résultats SonarQube

- **Qualité Gate**: PASSED ✅
- **Vulnérabilités critiques**: 0
- **Code Smells**: À analyser
- **Duplications**: 0%

## 🚀 Lancer le projet

```bash
git clone https://github.com/13ormatondo/devsecops-pipeline-complete.git
cd devsecops-pipeline-complete
docker compose up -d
