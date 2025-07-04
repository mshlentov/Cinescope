import time
from pathlib import Path

import allure
import pytest
from playwright.sync_api import sync_playwright

from tests.ui.pages.DetailsMoviePage import DetailsMoviePage
from tests.ui.pages.LoginPage import LoginPage



@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestDetailsMoviePage:
   @allure.title("Проведение успешного входа в систему")
   def test_review(self, registered_user, tmp_path):
        STORAGE_STATE = tmp_path / "auth_state.json"
        with sync_playwright() as playwright:
          # Запуск браузера с сохранением контекста
          browser = playwright.chromium.launch(headless=False)
          context = browser.new_context()
          page = context.new_page()

          login_page = LoginPage(page)
          details_movie_page = DetailsMoviePage(page)

          # Шаг 1: Авторизация
          login_page.open()
          login_page.login(registered_user["email"], registered_user["password"])

          # Проверка успешной авторизации
          login_page.assert_was_redirect_to_home_page()

          # Сохраняем состояние аутентификации
          context.storage_state(path=STORAGE_STATE)

          # Закрываем текущий контекст
          context.close()

          # Шаг 2: Создаем новый контекст с сохраненной аутентификацией
          context = browser.new_context(storage_state=STORAGE_STATE)
          page = context.new_page()
          details_movie_page = DetailsMoviePage(page)  # Переинициализируем с новой страницей

          # Шаг 3: Работаем на странице фильма
          details_movie_page.open()
          details_movie_page.write_review("Тестовый коммент")
          details_movie_page.select_rating("3")
          details_movie_page.submit_click()

          # Пауза для визуальной проверки
          time.sleep(5)

          # Закрываем браузер
          browser.close()