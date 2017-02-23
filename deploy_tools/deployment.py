from django.conf import settings as dj_settings

from fabric.api import cd, env, prefix, put, run

from .server import Server


class Deployment(object):

    def __init__(self, development):
        if development:
            self.server = Server(**{
                    "host": dj_settings.STAGING_HOST,
                    "user": dj_settings.STAGING_USER,
                    "website": dj_settings.STAGING_WEBSITE,
                    "project": dj_settings.PROJECT_NAME,
                    "development": development
                }
            )
        else:
            self.server = Server(**{
                    "host": dj_settings.PRODUCTION_HOST,
                    "user": dj_settings.PRODUCTION_USER,
                    "website": dj_settings.PRODUCTION_WEBSITE,
                    "project": dj_settings.PROJECT_NAME
                }
            )

    def deploy(self, initial, development):
        self.server.create_directories()
        self.server.get_latest_source(dj_settings.REPO_URL)
        self.update_secrets()
        self.server.update_virtualenv()
        self.server.update_static_files()
        self.server.update_database()

        if initial:
            self.server.set_nginx_config()
            self.server.disable_nginx_config("default")
            self.server.enable_nginx_config()

            self.server.set_gunicorn_config()
        else:
            self.server.reload_gunicorn()

        if development:
            self.run_tests()

    def run_tests(self):
        with cd(self.server.source_directory):
            with prefix('workon {}'.format(self.server.website)):
                for app in dj_settings.APPS_TO_TEST:
                    run('python manage.py test {}'.format(app))

    def update_secrets(self):
        secrets_directory = '{}/../secrets/secrets.json'
        put(
            secrets_directory.format(dj_settings.BASE_DIR), 
            secrets_directory.format(self.server.source_directory)
        )
