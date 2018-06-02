<template>
  <div class="app-layout">
    <div class="app-layout__header">
      <div class="app-layout__header__logo">
        <router-link
          :to="{ name: adminSession ? 'sessionsAdmin' : 'sessions' }">
          <img
            :src="logoImg"
            alt="logo">
        </router-link>
      </div>
      <slot name="user-info"/>
      <img
        :src="exitImg"
        class="app-layout__header__btn"
        @click="logoff">
    </div>
    <slot/>
  </div>
</template>

<script>
import { mapMutations, mapState } from 'vuex';
import exitImg from '../../../static/exit.svg';
import logoImg from '../../../static/logo.svg';
// import './public-path';

export default {
  name: 'AppLayout',
  data() {
    return {
      exitImg,
      logoImg,
    };
  },
  computed: mapState('common', ['adminSession']),
  methods: {
    ...mapMutations('common', ['unauthorize']),
    logoff() {
      this.unauthorize();
      this.$socket.sendObj({ type: 'close' });
    },
  },
};
</script>

<style lang="stylus">
.app-layout
  margin 10px
  padding-bottom: 40px;

  &__header
    display flex
    justify-content end
    align-items center

    &__logo
      flex 1

    &__btn
      cursor pointer
</style>
