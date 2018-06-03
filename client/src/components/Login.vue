<template>
  <div
    v-if="needLogin"
    class="login">
    <img
      :src="logoImg"
      class="login__logo"
      alt="logo">
    <form
      class="login__form">
      <input
        :class="{ login_failed: failed === 'username' }"
        v-model.trim="username"
        placeholder="Login"
        type="text">
      <input
        :class="{ login_failed: failed === 'password' }"
        v-model.trim="password"
        placeholder="password"
        type="password">
      <button
        type="submit"
        @click.prevent="login"
      >Войти</button>
    </form>
  </div>
</template>

<script>
import { setTimeout } from 'timers';
import { mapMutations, mapState } from 'vuex';
import logoImg from '../../static/logo.svg';

const API_URL = IS_PROD ? __webpack_public_path__ : 'http://ats-konstantin1:8080/';

export default {
  name: 'Login',
  data() {
    return {
      logoImg,
      username: '',
      password: '',
      failed: '',
      needLogin: false,
    };
  },
  computed: {
    ...mapState('common', ['adminSession', 'prevLoc']),
    credentials() {
      const { username, password } = this;
      return { username, password };
    },
  },
  created() {
    // проверим, может уже есть авторизационная кука
    fetch(`${API_URL}test_auth/`, { credentials: 'include' })
      .then(this.processAuth)
      .catch(err => console.error(err));
  },
  methods: {
    ...mapMutations('common', ['authorize']),
    processAuth(res) {
      switch (res.status) {
        case 200:
          res.text().then((username) => {
            this.authorize(username);
            this.$router.push({ name: this.adminSession ? 'sessionsAdmin' : 'sessions' });
            // this.$router.push(this.prevLoc && this.prevLoc.name === 'login' ? { name: this.adminSession ? 'sessionsAdmin' : 'sessions' } : this.prevLoc);
            this.$socket.sendObj({
              type: 'auth',
              msg: username,
            });
          });
          break;
        case 403:
          if (this.needLogin) {
            res.text().then((msg) => {
              this.failed = msg;
            });
          } else {
            this.needLogin = true;
          }

          setTimeout(() => {
            this.failed = false;
          }, 1000);
          break;
        default:
          throw new Error(`server responded with ${res.status}`);
      }
    },
    login() {
      const url = `${API_URL}login/`;
      const opts = {
        method: 'POST',
        body: JSON.stringify(this.credentials),
        credentials: 'include',
      };

      fetch(url, opts)
        .then(this.processAuth)
        .catch(() => {
          this.failed = true;
        });
    },
  },
};
</script>

<style lang="stylus">
.app-root
  height calc(100vh - 40px)
.login
  display grid
  grid-template-areas "login"
  justify-items center
  &__logo
    grid-area login
  &__form
    margin-top 10px
    width 100%
    & input, & button
      display block
      width 100%
      box-sizing border-box
      margin 5px 0

  &_failed
    border 2px solid white
    animation login-failed 1s linear

@keyframes login-failed
  0%
    border 2px solid red
  100%
    border 2px solid white

</style>
