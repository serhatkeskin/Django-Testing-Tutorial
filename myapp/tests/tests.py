from django.test import TestCase, TransactionTestCase, Client, tag
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.contrib.sessions.models import Session
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.db.utils import IntegrityError
from django.db import transaction, connection
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from myapp.views import home_view, login_view, logout_view
from myapp.models import MyModel, MyProduct
import unittest
import time

print("### connection.vendor: ", connection.vendor)  # Outputs 'sqlite', 'postgresql', 'mysql', etc.


class MyGeneralTestCase(TestCase):

    # region Client() vs HttpRequest()
    # ==============================================================================================================
    # ==============================================================================================================
    @unittest.skip("demonstrating skipping")
    def test_authenticate_with_credentials_using_client(self):
        user = User.objects.create_user(username="test", password="test")
        user.save()
        self.assertEqual(User.objects.count(), 1)  # check if user is created

        self.client.login(username="test", password="test")
        self.assertTrue(user.is_authenticated)  # check if user is authenticated

        response = self.client.get(reverse("home"))
        # region Debugging
        print("### Context Data: ", response.context)
        print("### response, ", response)
        print("### response.content, ", response.content.decode("utf-8"))
        # endregion

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Current user(request.user): test")

    """
        This is why we prefer Client over HttpRequest. Because HttpRequest does not have session support by default.
    """
    @unittest.skip("demonstrating skipping")
    def test_authenticate_with_credentials_using_http_request(self):
        user = User.objects.create_user(username="test", password="test")
        user.save()
        self.assertEqual(User.objects.count(), 1)  # check if user is created

        # Create a simulated HttpRequest
        request = HttpRequest()
        request.method = "POST"
        request.POST["username"] = "test"
        request.POST["password"] = "test"

        # Add session support to the request
        middleware = SessionMiddleware(lambda x: x)  # No-op get_response function
        middleware.process_request(request)
        print("### 1- session_count: ", Session.objects.count())
        request.session.save()
        print("### 2- session_count: ", Session.objects.count())

        # Call your custom login view
        response = login_view(request)

        # region Debugging
        print("### response, ", response)
        print("### request.session, ", request.session)
        # endregion

        # Assert the response is a redirect to 'home' upon successful login
        self.assertEqual(
            response.status_code, 302, "Login view should redirect to 'home'"
        )
        self.assertEqual(
            response.url,
            reverse("home"),
            "Login view should redirect to the correct 'home' URL",
        )
        # region check Session objects
        session_key = request.session.session_key
        try:
            session = Session.objects.get(session_key=session_key)
            self.assertIsNotNone(session, "Session should be created")
        except Session.DoesNotExist:
            self.fail(f"Session with key {session_key} was not found in the database.")
        session_user_id = request.session.get("_auth_user_id")
        self.assertIsNotNone(session_user_id, "Session should contain '_auth_user_id'")
        self.assertEqual(
            int(session_user_id),
            user.id,
            "Logged-in user ID should match the authenticated user",
        )

        print("### 3- session_count: ", Session.objects.count())
        print("### session: ", session)
        print("### session_key: ", session_key)
        print("### session_user_id: ", session_user_id)
        # endregion
    # ==============================================================================================================
    # ==============================================================================================================
    # endregion Client() vs HttpRequest()

    # region Testing Views
    # ==============================================================================================================
    # ==============================================================================================================
    @unittest.skip("demonstrating skipping")
    def test_home(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to my app")
    # ==============================================================================================================
    # ==============================================================================================================
    # endregion Testing Views

    # region Testing Models
    # ==============================================================================================================
    # ==============================================================================================================
    # @unittest.skip("demonstrating skipping")
    def test_create_model(self):
        MyModel.objects.create(name="test")
        self.assertEqual(MyModel.objects.count(), 1)
    # ==============================================================================================================
    # ==============================================================================================================
    # endregion Testing Models

    # region Decorators
    # ==============================================================================================================
    # ==============================================================================================================
    @unittest.skip("demonstrating skipping")
    def test_skip_decorator(self):
        self.assertEqual(1, 1)

    @unittest.skip("demonstrating skipping")
    @tag("fast")
    def test_fast(self):
        self.assertEqual(1, 1)

    # @unittest.skip("demonstrating skipping")
    @tag("slow")
    def test_slow(self):
        print("### Sleeping for 5 seconds(demonstrating slow test)")
        time.sleep(5)
        print("### Slept for 5 seconds")
        self.assertEqual(1, 1)


    # @unittest.skip("demonstrating skipping")
    @tag("slow", "api")
    def test_multiple_tags(self):
        print("### Sleeping for 5 seconds(demonstrating slow test)")
        time.sleep(5)
        print("### Slept for 5 seconds")
        self.assertEqual(1, 1)
    # ==============================================================================================================
    # ==============================================================================================================
    # endregion Decorators


class MyFixtureTestCase(TestCase):
    fixtures = ["myapp/tests/fixtures/my_fixture.json",]  # it simply calls the manage.py loaddata command with the given fixture file

    @unittest.skip("demonstrating skipping")
    def test_fixture_loaded(self):
        self.assertEqual(MyModel.objects.count(), 1)

    @unittest.skip("demonstrating skipping")
    def test_try_to_delete_loaded_fixture_forever(self):
        MyModel.objects.all().delete()
        self.assertEqual(MyModel.objects.count(), 0)

    @unittest.skip("demonstrating skipping")
    def test_if_fixture_deleted(self):
        # the fixture is loaded again before each test so the previous test does not affect this test
        # even if test_try_to_delete_loaded_fixture_forever test method is called after this test method
        print("\n### MyModel.objects.count(): ", MyModel.objects.count(), "\n", flush=True)
        self.assertEqual(MyModel.objects.count(), 1)

    # @unittest.skip("demonstrating skipping")
    def test_load_different_fixture(self):
        # Ensure initial fixture is loaded
        self.assertEqual(MyModel.objects.count(), 1, "Initial fixture should load 1 object.")

        # Load another fixture
        call_command("loaddata", "myapp/tests/fixtures/another_fixture.json")

        # Verify the total count of objects
        self.assertEqual(MyModel.objects.count(), 2, "Loading another fixture should add one more object.")

        # Verify objects from both fixtures
        try:
            obj_from_my_fixture = MyModel.objects.get(name="Test Object 1")
            obj_from_another_fixture = MyModel.objects.get(name="Test Object 2 - test different fixture")
        except MyModel.DoesNotExist as e:
            self.fail(f"Expected objects not found: {e}")

        # Assert specific attributes of the objects
        self.assertEqual(obj_from_my_fixture.name, "Test Object 1", "First object's name does not match.")
        self.assertEqual(
            obj_from_another_fixture.name,
            "Test Object 2 - test different fixture",
            "Second object's name does not match.",
        )


class MyFixtureTransactionTestCase(TransactionTestCase):
    fixtures = ["myapp/tests/fixtures/my_fixture.json",]  # it simply calls the manage.py loaddata command with the given fixture file

    # @unittest.skip("demonstrating skipping")
    def test_fixture_loaded(self):
        self.assertEqual(MyModel.objects.count(), 1)

    # @unittest.skip("demonstrating skipping")
    def test_a(self):
        count = MyModel.objects.count()
        print("### count: ", count)
        self.assertEqual(count, 1)
        MyModel.objects.all().delete()
        self.assertEqual(MyModel.objects.count(), 0)

    # @unittest.skip("demonstrating skipping")
    def test_try_to_delete_loaded_fixture_forever(self):
        count = MyModel.objects.count()
        print("### count: ", count)
        self.assertEqual(count, 1)
        MyModel.objects.all().delete()
        self.assertEqual(MyModel.objects.count(), 0)

    # @unittest.skip("demonstrating skipping")
    def test_if_fixture_deleted(self):
        # the fixture is loaded again before each test so the previous test does not affect this test
        # even if test_try_to_delete_loaded_fixture_forever test method is called after this test method
        print("\n### MyModel.objects.count(): ", MyModel.objects.count(), "\n", flush=True)
        self.assertEqual(MyModel.objects.count(), 1)

    # @unittest.skip("demonstrating skipping")
    def test_load_different_fixture(self):
        # Ensure initial fixture is loaded
        self.assertEqual(MyModel.objects.count(), 1, "Initial fixture should load 1 object.")

        # Load another fixture
        call_command("loaddata", "myapp/tests/fixtures/another_fixture.json")

        # Verify the total count of objects
        self.assertEqual(MyModel.objects.count(), 2, "Loading another fixture should add one more object.")

        # Verify objects from both fixtures
        try:
            obj_from_my_fixture = MyModel.objects.get(name="Test Object 1")
            obj_from_another_fixture = MyModel.objects.get(name="Test Object 2 - test different fixture")
        except MyModel.DoesNotExist as e:
            self.fail(f"Expected objects not found: {e}")

        # Assert specific attributes of the objects
        self.assertEqual(obj_from_my_fixture.name, "Test Object 1", "First object's name does not match.")
        self.assertEqual(
            obj_from_another_fixture.name,
            "Test Object 2 - test different fixture",
            "Second object's name does not match.",
        )
    
    def test_try_to_delete_loaded_fixture_forever_v2(self):
        count = MyModel.objects.count()
        print("### count: ", count)
        self.assertEqual(count, 1)
        MyModel.objects.all().delete()
        self.assertEqual(MyModel.objects.count(), 0)


class My_setUp_and_tearDown_TestCase(TestCase):
    fixtures = ["myapp/tests/fixtures/my_fixture.json",]  # it simply calls the manage.py loaddata command with the given fixture file

    def setUp(self):
        # print("\n### setUp() is called\n", flush=True)
        self.user = User.objects.create_user(username="test", password="test")
        self.user.save()

    def tearDown(self):
        # print("\n### tearDown() is called\n", flush=True)
        # self.user.delete()
        pass

    @unittest.skip("demonstrating skipping")
    def test_setUp_called(self):
        self.assertEqual(User.objects.count(), 1)


class MyTransactionTestCase(TransactionTestCase):
    fixtures = ["myapp/tests/fixtures/my_fixture.json",]  # it simply calls the manage.py loaddata command with the given fixture file

    def setUp(self):
        # print("\n### setUp() is called\n", flush=True)
        self.user = User.objects.create_user(username="test", password="test")
        self.user.save()

    def tearDown(self):
        # print("\n### tearDown() is called\n", flush=True)
        # self.user.delete()
        pass

    @unittest.skip("demonstrating skipping")
    def test_setUp_called(self):
        self.assertEqual(User.objects.count(), 1)

    @unittest.skip("demonstrating skipping")
    def test_fixture_loaded(self):
        self.assertEqual(MyModel.objects.count(), 1)


class Test_TestCaseBehavior(TestCase):
    # @unittest.skip("demonstrating skipping")
    def test_unique_unique_code_constraint(self):
        """
        The second create statement in this test does not raise an IntegrityError
        because the unique constraint isn’t checked until the transaction is committed 
        (which happens after the test).
        """
        MyProduct.objects.create(name="Product A", unique_code="SKU001")
        with self.assertRaises(IntegrityError):  # Should not raise IntegrityError here, # WARNING but it does in sqlite!!
            MyProduct.objects.create(name="Product B", unique_code="SKU001")

    # @unittest.skip("demonstrating skipping")
    def test_atomic_block(self):
        # <<< Start of implicit atomic block >>> #
        self.assertFalse(transaction.get_autocommit(), "Test is not in an atomic block!")
        MyProduct.objects.create(name="Product A", unique_code="SKU001")
        try:
            MyProduct.objects.create(name="Product B", unique_code="SKU001")
        except IntegrityError:
            if connection.needs_rollback:
                print("Transaction is broken. Needs rollback.")
                # connection.rollback() ## cannot rollback. This is forbidden when an 'atomic' block is active.
            pass
        self.assertEqual(MyProduct.objects.count(), 0)  
        # it should be 0 because the transaction is rolled back due to IntegrityError, BUT INSTEAD in sqlite...
        # ...it throws an error. "You can't execute queries until the end of the 'atomic' block."
        # Because the whole code is in an atomic block and it marked as broken query because of the error
        # and cannot do queries in broken status.

        # <<< End of implicit atomic block >>> #

        # At the end of this test, the transaction will be rolled back
        # The database remains unchanged

    # @unittest.skip("demonstrating skipping")
    def test_slug_generation(self):
        """
        Test that the signal generates a slug before saving.
        """
        product = MyProduct.objects.create(name="Test Product", unique_code="SKU001")
        self.assertEqual(product.slug, "test-product")


class Test_TransactionTestCaseBehavior(TransactionTestCase):
    # @unittest.skip("demonstrating skipping")
    def test_unique_unique_code_constraint(self):
        MyProduct.objects.create(name="Product A", unique_code="SKU001")
        with self.assertRaises(IntegrityError):  # Raises IntegrityError
            MyProduct.objects.create(name="Product B", unique_code="SKU001")

    # @unittest.skip("demonstrating skipping")
    def test_no_atomic_block(self):
        # No implicit atomic block here
        self.assertTrue(transaction.get_autocommit(), "Test is in an atomic block!")

        MyProduct.objects.create(name="Product A", unique_code="SKU001") # This will be committed immediately to the database
        try:
            MyProduct.objects.create(name="Product B", unique_code="SKU001")
        except IntegrityError:
            pass
        self.assertEqual(MyProduct.objects.count(), 1)  # it should be 1 because the first query is committed

        # The changes remain committed during the test

    # @unittest.skip("demonstrating skipping")
    def test_slug_generation(self):
        """
        Test that the signal generates a slug before saving.
        """
        product = MyProduct.objects.create(name="Another Product", unique_code="SKU002")
        self.assertEqual(product.slug, "another-product")


class MyFunctionalTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # Path to chromedriver
        webdriver_path = "webdriver/mac_arm/chromedriver"  # Change this to your correct path

        # Configure ChromeOptions
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model which is not supported in Docker

        # Set up Chrome driver with Service and Options
        self.browser = webdriver.Chrome(
            service=Service(webdriver_path),
            options=chrome_options
        )

    def tearDown(self):
        self.browser.quit()

    # @unittest.skip("demonstrating skipping")
    def test_home_page(self):
        self.browser.get(self.live_server_url + reverse("home"))
        time.sleep(3)
        self.assertIn("Welcome to my app", self.browser.page_source)

    # @unittest.skip("demonstrating skipping")
    def test_login_page(self):
        self.browser.get(self.live_server_url + reverse("login"))
        time.sleep(3)
        self.assertIn("Login", self.browser.page_source)

    # @unittest.skip("demonstrating skipping")
    def test_login(self):
        # Create a user
        user = User.objects.create_user(username="test", password="test")
        self.assertEqual(User.objects.count(), 1)  # check if user is created

        self.browser.get(self.live_server_url + reverse("login"))
        time.sleep(3)
        # Interact with the login form
        self.browser.find_element(By.NAME, 'username').send_keys('test')
        self.browser.find_element(By.NAME, 'password').send_keys('test')
        self.browser.find_element(By.NAME, 'submit').click()
        time.sleep(3)

        # Check if the user is redirected to the home page
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("home"))
        # Check if the user is logged in and the username is displayed
        self.assertIn("Current user(request.user): test", self.browser.page_source)

        # print("### self.browser.current_url: ", self.browser.current_url)
        # print("### self.browser./: ", self.browser.page_source)
