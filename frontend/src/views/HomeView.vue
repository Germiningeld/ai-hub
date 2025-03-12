<template>
  <div class="home-view">
    <div class="container">
      <header class="py-5 text-center">
        <div class="mb-4">
          <!-- Здесь позже будет логотип -->
          <div class="display-6 fw-bold text-primary">AIHub</div>
        </div>
        <h1 class="display-4 fw-bold mb-4">Универсальный интерфейс для ИИ-моделей</h1>
        <p class="lead col-lg-8 mx-auto">
          AIHub — это единая платформа для взаимодействия с различными ИИ-моделями через интуитивно понятный интерфейс.
          Оптимизируйте расходы, управляйте промптами и получайте аналитику использования.
        </p>
        <div class="d-flex justify-content-center gap-3 mt-4">
          <router-link to="/login" class="btn btn-primary btn-lg px-4">
            Войти в систему
          </router-link>
          <router-link to="/register" class="btn btn-outline-secondary btn-lg px-4">
            Регистрация
          </router-link>
        </div>
      </header>

      <div class="features py-5">
        <h2 class="text-center mb-5">Основные возможности</h2>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card p-4 bg-light rounded h-100">
              <div class="feature-icon mb-3 text-primary">
                <i class="bi bi-intersect fs-1"></i>
              </div>
              <h3 class="h5">Единый интерфейс</h3>
              <p>Доступ к различным ИИ-моделям через единую точку входа, без необходимости переключения между сервисами.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 bg-light rounded h-100">
              <div class="feature-icon mb-3 text-primary">
                <i class="bi bi-cash-coin fs-1"></i>
              </div>
              <h3 class="h5">Экономия средств</h3>
              <p>Снижение затрат до 30-50% за счет оптимизации использования и кэширования повторяющихся запросов.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 bg-light rounded h-100">
              <div class="feature-icon mb-3 text-primary">
                <i class="bi bi-lightning fs-1"></i>
              </div>
              <h3 class="h5">Библиотека промптов</h3>
              <p>Создавайте, сохраняйте и организуйте эффективные промпты для повышения продуктивности работы с ИИ.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 bg-light rounded h-100">
              <div class="feature-icon mb-3 text-primary">
                <i class="bi bi-bar-chart fs-1"></i>
              </div>
              <h3 class="h5">Аналитика использования</h3>
              <p>Детальные отчеты о затратах, использовании токенов и эффективности различных моделей для ваших задач.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 bg-light rounded h-100">
              <div class="feature-icon mb-3 text-primary">
                <i class="bi bi-folder fs-1"></i>
              </div>
              <h3 class="h5">Организация тредов</h3>
              <p>Группируйте треды по категориям и темам для удобного доступа и эффективного управления историей.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card p-4 bg-light rounded h-100">
              <div class="feature-icon mb-3 text-primary">
                <i class="bi bi-shield-check fs-1"></i>
              </div>
              <h3 class="h5">Безопасность данных</h3>
              <p>Все ваши запросы и ответы хранятся локально, обеспечивая полный контроль над вашими данными.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="cta-section py-5 my-5 text-center bg-light rounded">
        <h2 class="mb-4">Готовы оптимизировать работу с ИИ?</h2>
        <p class="lead mb-4">Присоединяйтесь к AIHub сегодня и начните экономить время и деньги</p>
        <router-link to="/register" class="btn btn-primary btn-lg px-5">
          Начать бесплатно
        </router-link>
      </div>

      <div class="how-it-works py-5">
        <h2 class="text-center mb-5">Как это работает</h2>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="step text-center">
              <div class="step-number bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                <span>1</span>
              </div>
              <h3 class="h5">Регистрация и настройка</h3>
              <p>Создайте аккаунт и добавьте свои API-ключи от провайдеров ИИ (OpenAI, Anthropic и др.)</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="step text-center">
              <div class="step-number bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                <span>2</span>
              </div>
              <h3 class="h5">Выбор модели</h3>
              <p>Выберите подходящую модель для вашей задачи из единого интерфейса</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="step text-center">
              <div class="step-number bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                <span>3</span>
              </div>
              <h3 class="h5">Взаимодействие и анализ</h3>
              <p>Общайтесь с ИИ и отслеживайте статистику использования в реальном времени</p>
            </div>
          </div>
        </div>
      </div>

      <footer class="pt-5 mt-5 border-top">
        <div class="row">
          <div class="col-md-6 mb-3">
            <h5>AIHub</h5>
            <p class="text-muted">© 2024 — Все права защищены</p>
          </div>
          <div class="col-md-6 text-md-end">
            <ul class="list-inline">
              <li class="list-inline-item"><a href="#" class="text-decoration-none">Условия использования</a></li>
              <li class="list-inline-item"><a href="#" class="text-decoration-none">Конфиденциальность</a></li>
              <li class="list-inline-item"><a href="#" class="text-decoration-none">О нас</a></li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

onMounted(() => {
  // Проверка аутентификации
  const token = localStorage.getItem('auth_token');
  if (token) {
    // Если пользователь уже авторизован, перенаправляем на страницу чатов
    router.push('/chat');
  }
});
</script>

<style scoped>
.home-view {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.step-number {
  width: 50px;
  height: 50px;
  font-size: 1.5rem;
  font-weight: bold;
}

.cta-section {
  padding: 3rem;
}

footer {
  padding-bottom: 2rem;
}
</style>