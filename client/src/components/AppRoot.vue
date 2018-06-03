<template>
  <div
    :class="gridLayout"
    class="app-root">
    <server-state-indicator/>
    <router-view/>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import ServerStateIndicator from './ServerStateIndicator.vue';

export default {
  name: 'AppRoot',
  components: {
    ServerStateIndicator,
  },
  computed: {
    ...mapState('common', ['authorized']),
    gridLayout() {
      return {
        'app-root_grid-layout': !this.authorized,
      };
    },
  },
  created() {
    // console.log(this.$store.watch)
    this.$store.watch(this.watchAuth);
    this.$store.$cookie = this.$cookie;
    this.$store.$socket = this.$socket;
    // if (!this.authorized) {
    //   this.$router.push({ name: 'login' });
    // }
  },
  methods: {
    watchAuth(state) {
      if (!state.common.authorized) {
        // this.$store.commit('common/prevLoc', {
        //   name: this.$route.name,
        //   params: { ...this.$route.params },
        // });
        this.$router.push({ name: 'login' });
      }
    },
  },
};
</script>

<!-- CSS libraries -->
<style src="normalize.css/normalize.css"></style>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style src="../tooltip.css"></style>
<style src="../vm-tabs.css"></style>
<style src="../sprites.css"></style>

<!-- Global CSS -->
<style>
  * {
    font-family: 'Open Sans', sans-serif;
  }

  body {
    background: rgb(250,250,250);
    padding: 0 16px 40px;
  }

  code {
    font-family: Menlo, Monaco, Lucida Console, Liberation Mono, DejaVu Sans Mono,
      Bitstream Vera Sans Mono, Courier New, monospace, serif;
    /* font-size: 0.9em; */
    white-space: pre-wrap;
    color: #2c3e50;
  }

</style>

<style lang="stylus">
.app-root
  display grid
  &_grid-layout
    grid-template-areas "app-root"
    justify-content center
    align-content center

// позиционирование блоков
.server-state-indicator
  position fixed
  right 10px
  bottom 10px

.login
  grid-area app-root
</style>
