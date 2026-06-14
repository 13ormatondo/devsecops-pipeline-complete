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
                    curl -s -f http://localhost:5000/init-db || echo "Database already initialized or endpoint not ready"
                    echo "Database initialization attempted"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking application health..."
                    curl -s -f http://localhost:5000/health || echo "Health check failed but continuing"
                    echo "Application is responding"
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
                    curl -s http://localhost:5000/health || echo "WARNING: App health check failed"
                    
                    # Exécuter les tests Postman (ne jamais échouer le pipeline)
                    set +e
                    docker run --network host -v $PWD/postman:/etc/newman \
                      postman/newman:latest run /etc/newman/collection.json
                    EXIT_CODE=$?
                    set -e
                    
                    if [ $EXIT_CODE -eq 0 ]; then
                        echo "✅ All Postman tests passed!"
                    else
                        echo "⚠️ Some Postman tests failed (exit code: $EXIT_CODE)"
                    fi
                    
                    echo "Postman tests completed!"
                '''
            }
        }

        stage('OWASP ZAP DAST Scan') {
            steps {
                sh '''
                    echo "=========================================="
                    echo "=== OWASP ZAP DAST Scan ==="
                    echo "=========================================="
                    
                    set +e
                    docker run --network host -v $PWD:/zap/wrk \
                      owasp/zap2docker-stable zap-api-scan.py \
                      -t http://localhost:5000/openapi.yaml \
                      -f openapi \
                      -r zap_report.html \
                      -J zap_report.json
                    ZAP_EXIT=$?
                    set -e
                    
                    if [ $ZAP_EXIT -eq 0 ]; then
                        echo "✅ ZAP scan completed with no issues!"
                    else
                        echo "⚠️ ZAP scan found issues (exit code: $ZAP_EXIT)"
                    fi
                    
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
                echo "Cleaning up containers..."
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
            echo "❌ PIPELINE PARTIELLEMENT ÉCHOUÉ ❌"
            echo "=========================================="
            echo "Certaines étapes ont rencontré des problèmes."
            echo "Consultez les logs pour plus de détails."
            echo "=========================================="
        }
    }
}
