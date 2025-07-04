import allure
import pytest

from db_requester.models import AccountTransactionTemplate, MovieDBModel
from utils.data_generator import DataGenerator


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session):
        stan_name = f"Stan_{DataGenerator.generate_random_int(10)}"
        bob_name = f"Bob_{DataGenerator.generate_random_int(10)}"

        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=stan_name, balance=1000)
            bob = AccountTransactionTemplate(user=bob_name, balance=500)
            db_session.add_all([stan, bob])
            db_session.commit()

        def transfer_money(session, from_user, to_user, amount):
            with allure.step("Получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_user).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_user).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()
            return from_account, to_account

        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000
            assert bob.balance == 500

        try:
            with allure.step("Выполняем перевод 200 единиц от stan к bob"):
                updated_stan, updated_bob = transfer_money(
                    db_session,
                    from_user=stan_name,
                    to_user=bob_name,
                    amount=200
                )

            with allure.step("Проверяем, что балансы изменились"):
                assert updated_stan.balance == 800
                assert updated_bob.balance == 700

        except Exception as e:
            with allure.step("ОШИБКА откаты транзакции"):
                db_session.rollback()
            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.query(AccountTransactionTemplate).filter(
                    AccountTransactionTemplate.user.in_([stan_name, bob_name])
                ).delete(synchronize_session=False)
                db_session.commit()


# Тесты для DELETE /movies/{id}
def test_delete_movie_positive(create_test_movie, super_admin, db_session):
    """
    Позитивный тест удаления фильма
    """

    movie_id = "1450"

    movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id)

    if movies_from_db.count() == 0:
        # Создаем фильм для теста
        response = create_test_movie.json()
        movie_id = response["id"]

    movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id)
    assert movies_from_db.count() == 1, "В базе уже присутствует фильм с таким названием"

    # Удаляем фильм
    super_admin.api.movies_api.delete_movie(movie_id)

    # Проверяем, что фильм удален
    super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)

    # проверяем что в конце тестирования фильма с таким названием действительно нет в базе
    movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id)
    assert movies_from_db.count() == 0, "Фильм не был удален из базы!"


# Шапка страницы
        def go_to_home_page(self):
            """Переход на главную страницу."""
            self.page.click(self.home_button)
            self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")  # Ожидание загрузки главной страницы

        def go_to_all_movies(self):
            """Переход на страницу 'Все фильмы'."""
            self.page.click(self.all_movies_button)
            self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")  # Ожидание загрузки страницы

        # Тело страницы
        def open(self):
            """Переход на страницу регистрации."""
            self.page.goto(self.url)

        def enter_full_name(self, full_name: str):
            """Ввод full_name"""
            self.page.fill(self.full_name_input, full_name)

        def enter_email(self, email: str):
            """Ввод email"""
            self.page.fill(self.email_input, email)

        def enter_password(self, password: str):
            """Ввод пароля"""
            self.page.fill(self.password_input, password)

        def enter_repeat_password(self, password: str):
            """Ввод подтверждения пароля"""
            self.page.fill(self.repeat_password_input, password)

        def click_register_button(self):
            """Клик по кнопке регистрации"""
            self.page.click(self.register_button)

        # Вспомогательные action методы
        def register(self, full_name: str, email: str, password: str, confirm_password: str):
            """Полный процесс регистрации."""
            self.enter_full_name(full_name)
            self.enter_email(email)
            self.enter_password(password)
            self.enter_repeat_password(confirm_password)
            self.click_register_button()

        def wait_redirect_to_login_page(self):
            """Переход на страницу login."""
            self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/login")  # Ожидание загрузки страницы login
            assert self.page.url == "https://dev-cinescope.coconutqa.ru/login", "Редирект на домашнюю старницу не произошел"

        def check_allert(self):
            """Проверка всплывающего сообщения после редиректа"""
            # Проверка появления алерта с текстом "Подтвердите свою почту"
            notification_locator = self.page.get_by_text("Подтвердите свою почту")
            notification_locator.wait_for(state="visible")  # Ждем появления элемента

            assert notification_locator.is_visible(), "Уведомление не появилось"
            # Ожидание исчезновения алерта
            notification_locator.wait_for(state="hidden")  # Ждем, пока алерт исчезнет
            assert notification_locator.is_visible() == False, "Уведомление исчезло"