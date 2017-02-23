from django.conf import settings
from django.test import TestCase

from mock import patch

from deploy_tools.deployment import Deployment


class TestDeployment(TestCase):

    def settings_for_tests(self):
        return {
            "REPO_URL": "repo_test",
            "APPS_TO_TEST": ["apps_test"],
            "PROJECT_NAME": "project_test",

            "STAGING_HOST": "staging_host",
            "STAGING_USER": "staging_user",
            "STAGING_WEBSITE": "staging_website",

            "PRODUCTION_HOST": "production_host",
            "PRODUCTION_USER": "production_user",
            "PRODUCTION_WEBSITE": "production_website",
        }

    @patch("deploy_tools.deployment.Server")
    def test_init_if_deployment(self, server):
        with self.settings(**self.settings_for_tests()):
            deployment = Deployment(True)

            server.assert_called_once_with(**{
                    "host": "staging_host",
                    "user": "staging_user",
                    "website": "staging_website",
                    "project": "project_test",
                    "development": True,
                }
            )

    @patch("deploy_tools.deployment.Server")
    def test_init_if_not_deployment(self, server):
        with self.settings(**self.settings_for_tests()):
            deployment = Deployment(False)

            server.assert_called_once_with(**{
                    "host": "production_host",
                    "user": "production_user",
                    "website": "production_website",
                    "project": "project_test"
                }
            )
