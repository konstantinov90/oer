<template>
  <div class="app-layout">
    <div class="app-layout__header">
      <div class="app-layout__header__logo">
        <router-link
          :to="{ name: adminSession ? 'sessionsAdmin' : 'sessions' }">
          <img
            src="/static/logo.svg"
            alt="logo">
        </router-link>
      </div>
      <slot name="user-info"/>
      <img
        class="app-layout__header__btn"
        src="/static/exit.svg"
        @click="logoff">
    </div>
    <slot/>
  </div>
</template>

<script>
import { mapMutations, mapState } from 'vuex';

export default {
  name: 'AppLayout',
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

  &__header
    display flex
    justify-content end
    align-items center

    & *
      margin 0 10px

    &__logo
      flex 1

    &__btn
      cursor pointer
</style>
