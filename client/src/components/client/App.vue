<template>
  <app-layout>
    <template slot="user-info">
      <user-info-view />
    </template>
    <div class="app__grid">
      <router-view/>
    </div>
  </app-layout>
</template>

<script>
import { mapState } from 'vuex';
import AppLayout from '../common/AppLayout.vue';
import UserInfoView from './UserInfoView.vue';

export default {
  name: 'App',
  components: {
    AppLayout,
    UserInfoView,
  },
  computed: {
    ...mapState('common', ['phase']),
  },
};
</script>

<!-- Scoped component css -->
<!-- It only affect current component -->
<style scoped>

</style>
