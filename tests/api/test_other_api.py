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