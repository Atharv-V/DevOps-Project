pipeline {
    agent any

    environment {
        // Define any environment variables if needed, like Python or Node versions
        PYTHON_ENV = '/usr/bin/python3'  // Adjust to your python path
        NODE_ENV = '/usr/bin/node'  // Adjust to your node path
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Clone the repository
                git 'https://github.com/Atharv-V/DevOps-Project.git'
            }
        }

        stage('Install Dependencies - Backend') {
            steps {
                // Navigate to the backend directory and install Python dependencies
                script {
                    dir('model/HMM') {
                        sh '''
                            python3 -m venv venv
                            source venv/bin/activate
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Run Python Model') {
            steps {
                // Run the Python model
                script {
                    dir('model/HMM') {
                        sh 'python app.py'
                    }
                }
            }
        }

        stage('Install Dependencies - Frontend') {
            steps {
                // Navigate to the frontend directory and install Node.js dependencies
                script {
                    dir('frontend') {
                        sh 'npm install'
                    }
                }
            }
        }

        stage('Run Frontend') {
            steps {
                // Run the frontend using Node
                script {
                    dir('frontend') {
                        sh 'node start'
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Build and deployment were successful!'
        }
        failure {
            echo 'Build or deployment failed.'
        }
    }
}
