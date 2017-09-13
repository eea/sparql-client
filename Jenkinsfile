pipeline {
  agent any

  environment {
        GIT_NAME = "sparql-client"
    }

  stages {
    stage('Tests') {
      steps {
        parallel(

          "WWW": {
            node(label: 'docker-1.13') {
              sh '''
NAME="$BUILD_TAG-www"
docker run -i --net=host --name="$NAME" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" eeacms/www-devel /debug.sh bin/test -v -vv -s $GIT_NAME
docker rm -v $NAME'''
            }
          },

          "KGS": {
            node(label: 'docker-1.13') {
              sh '''
NAME="$BUILD_TAG-kgs"
docker run -i --net=host --name="$NAME" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" eeacms/kgs-devel /debug.sh bin/test --test-path /plone/instance/src/$GIT_NAME -v -vv -s $GIT_NAME
docker rm -v $NAME'''
            }
          },

          "Plone4": {
            node(label: 'docker-1.13') {
              sh '''
NAME="$BUILD_TAG-plone4"
docker run -i --net=host --name="$NAME" -v /plone/instance/parts -e GIT_BRANCH="$BRANCH_NAME" -e ADDONS="$GIT_NAME" -e DEVELOP="src/$GIT_NAME" eeacms/plone-test:4 -v -vv -s $GIT_NAME
docker rm -v $NAME'''
            }
          }
        )
      }
    }

    stage('Code Analysis') {
      steps {
        parallel(

          "ZPT Lint": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-zptlint"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/zptlint
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                  throw err
                }
              }
            }
          },

          "JS Lint": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-jslint"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/jslint4java
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                  throw err
                }
              }
            }
          },

          "PyFlakes": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-pyflakes"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/pyflakes
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                  throw err
                }
              }
            }
          },

          "i18n": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-i18n"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name=$NAME -e GIT_SRC="$GIT_SRC" eeacms/i18ndude
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                  throw err
                }
              }
            }
          }
        )
      }
    }

    stage('Code Syntax') {
      steps {
        parallel(

          "JS Hint": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-jshint"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/jshint
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                }
              }
            }
          },

          "CSS Lint": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-csslint"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/csslint
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                }
              }
            }
          },

          "PEP8": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-pep8"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/pep8
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                }
              }
            }
          },


          "PyLint": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''
NAME="$BUILD_TAG-pylint"
GIT_SRC="https://github.com/eea/$GIT_NAME.git --branch=$BRANCH_NAME"
docker run -i --net=host --name="$NAME" -e GIT_SRC="$GIT_SRC" eeacms/pylint
docker rm -v $NAME'''
                } catch (err) {
                  echo "Unstable: ${err}"
                }
              }
            }
          }

        )
      }
    }

  }

  post {
    changed {
      script {
        def url = "${env.BUILD_URL}/display/redirect"
        def status = currentBuild.currentResult
        def subject = "${status}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
        def summary = "${subject} (${url})"
        def details = """<h1>${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${status}</h1>
                         <p>Check console output at <a href="${url}">${env.JOB_BASE_NAME} - #${env.BUILD_NUMBER}</a></p>
                      """

        def color = '#FFFF00'
        if (status == 'SUCCESS') {
          color = '#00FF00'
        } else if (status == 'FAILURE') {
          color = '#FF0000'
        }
        slackSend (color: color, message: summary)
        emailext (subject: '$DEFAULT_SUBJECT', to: '$DEFAULT_RECIPIENTS', body: details)
      }
    }
  }
}            
