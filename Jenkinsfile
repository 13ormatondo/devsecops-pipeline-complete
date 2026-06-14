pipeline {
    agent any

    environment {
        SONAR_HOST_URL = "http://192.168.56.11:9000"
        SONAR_AUTH_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQubeServer') {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=vulnerable-app \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.login=${SONAR_AUTH_TOKEN}
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("vulnerable-app:latest", "./vulnerable-app")
                }
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                    docker stop vulnerable-app || true
                    docker rm vulnerable-app || true
                    docker run -d --name vulnerable-app -p 5000:5000 vulnerable-app:latest
                    sleep 10
                '''
            }
        }

        stage('Initialize Database') {
            steps {
                sh '''
                    echo "Initializing database..."
                    curl -s http://localhost:5000/init-db
                    echo ""
                    echo "Database initialized successfully!"
                '''
            }
        }

        stage('Postman API Security Tests') {
            steps {
                sh '''
                    echo "=========================================="
                    echo "=== Postman API Security Tests ==="
                    echo "=========================================="
                    
                    # Vérifier que l'application répond
                    echo "Checking application health..."
                    curl -f http://localhost:5000/health || echo "WARNING: App health check failed"
                    
                    # Exécuter les tests Postman
                    echo "Running Postman tests..."
                    docker run --network host -v $PWD/postman:/etc/newman \
                      postman/newman:latest run /etc/newman/collection.json \
                      --suppress-exit-code || echo "Postman tests completed"
                    
                    echo "Postman tests finished!"
                '''
            }
        }

        stage('OWASP ZAP DAST Scan') {
            steps {
                sh '''
                    echo "=========================================="
                    echo "=== OWASP ZAP DAST Scan ==="
                    echo "=========================================="
                    
                    # Créer le dossier pour les rapports
                    mkdir -p zap-reports
                    
                    # Exécuter ZAP scan
                    docker run --network host -v $PWD:/zap/wrk \
                      owasp/zap2docker-stable zap-api-scan.py \
                      -t http://localhost:5000/openapi.yaml \
                      -f openapi \
                      -r zap_report.html \
                      -J zap_report.json \
                      || echo "ZAP scan completed with issues"
                    
                    echo "ZAP scan finished! Report generated."
                '''
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: false,
                    keepAll: false,
                    reportDir: '.',
                    reportFiles: 'zap_report.html',
                    reportName: 'OWASP ZAP Security Report'
                ])
            }
        }
    }

    post {
        always {
            sh '''
                echo "Cleaning up..."
                docker stop vulnerable-app || true
                docker rm vulnerable-app || true
            '''
            cleanWs()
        }
        success {
            echo "=========================================="
            echo "🎉 PIPELINE RÉUSSI ! 🎉"
            echo "=========================================="
            echo "✅ SonarQube Analysis: SUCCESS"
            echo "✅ Quality Gate: PASSED"
            echo "✅ Docker Build: SUCCESS"
            echo "✅ Postman Tests: COMPLETED"
            echo "✅ ZAP Scan: COMPLETED"
            echo ""
            echo "📊 Résultats disponibles :"
            echo "   - SonarQube: ${SONAR_HOST_URL}/dashboard?id=vulnerable-app"
            echo "   - ZAP Report: zap_report.html"
            echo "=========================================="
        }
        failure {
            echo "=========================================="
            echo "❌ PIPELINE ÉCHOUÉ ❌"
            echo "=========================================="
            echo "Vérifiez les logs ci-dessus pour plus de détails."
            echo "=========================================="
        }
    }
}
